import boto3
from botocore.config import Config
import btc2fiat
import click
from datetime import datetime, timedelta
import dateutil.parser
from flask import Flask, jsonify, request, send_file
from flask.cli import with_appcontext
from flask_migrate import Migrate
from functools import wraps
import hashlib
import io
from itertools import chain
import json
import jwt
import lndgrpc
import logging
from logging.config import dictConfig
import magic
import math
from nostr.event import Event, EncryptedDirectMessage
from nostr.key import PrivateKey
from nostr.relay_manager import RelayManager
import os
import random
import requests
from requests_oauthlib import OAuth1Session
from requests.exceptions import JSONDecodeError
import signal
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
import string
import sys
import time

from extensions import cors, db
from utils import sats2usd, usd2sats

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    'handlers': {'default': {
        'class': 'logging.StreamHandler',
        'formatter': 'default',
    }},
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['default'],
    },
})

class MyFlask(Flask):
    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)
        self.initialized = False

    def __call__(self, environ, start_response):
        if not self.initialized:
            from api import api_blueprint
            app.register_blueprint(api_blueprint)
            self.initialized = True
        return super().__call__(environ, start_response)

def create_app():
    app = MyFlask(__name__, static_folder="../web/static")
    app.config.from_object('config')
    cors.init_app(app)
    db.init_app(app)
    return app

app = create_app()

import models as m

migrate = Migrate(app, db)

@app.cli.command("run-tests")
@with_appcontext
def run_tests():
    app.logger.setLevel(getattr(logging, LOG_LEVEL))
    signal.signal(signal.SIGTERM, lambda _, __: sys.exit(0))

    import unittest
    import api_tests
    suite = unittest.TestLoader().loadTestsFromModule(api_tests)
    unittest.TextTestRunner().run(suite)

@app.cli.command("finalize-auctions")
def finalize_auctions():
    app.logger.setLevel(getattr(logging, LOG_LEVEL))
    signal.signal(signal.SIGTERM, lambda _, __: sys.exit(0))

    app.logger.info("Starting finalize-auctions process...")

    while True:
        try:
            btc2usd = btc2fiat.get_value('kraken')
        except Exception:
            app.logger.error("Error fetching the exchange rate! Taking a 1 minute nap...")
            time.sleep(60)
            continue
        for auction in db.session.query(m.Auction).filter((m.Auction.end_date <= datetime.utcnow()) & (m.Auction.has_winner == None)):
            app.logger.info(f"Looking at {auction.id=}...")

            top_bid = auction.get_top_bid()

            while top_bid and db.session.query(m.Sale).filter_by(auction_id=auction.id, buyer_id=top_bid.buyer_id, state=m.SaleState.EXPIRED.value).first():
                app.logger.info(f"Skipping bidder {top_bid.buyer_id} with expired sale for {auction.id=} and picking the next one!")
                top_bid = auction.get_top_bid(below=top_bid.amount)

            if not top_bid or not auction.reserve_bid_reached:
                app.logger.info(f"Auction {auction.id=} has no winner!")
                auction.has_winner = False
                auction.winning_bid_id = None
                db.session.commit()
                continue

            app.logger.info(f"Auction {auction.id=} has a winner: user.id={top_bid.buyer_id}!")
            auction.has_winner = True
            auction.winning_bid_id = top_bid.id

            quantity = 1 # always 1 for auctions

            try:
                if auction.campaign:
                    address = auction.campaign.get_new_address()
                else:
                    address = auction.item.seller.get_new_address()
            except m.AddressGenerationError as e:
                app.logger.error(f"{auction.id=} " + str(e))
                # NB: here we commit because we want has_winner and winning_bid_id to be set,
                # so we never touch this auction again and simply skip generating the corresponding sale
                # there is really nothing else we can do at this point for this auction,
                # but at least we picked a winner and stop retrying!
                db.session.commit()
                continue
            except MempoolSpaceError as e:
                app.logger.error(str(e) + " Taking a 1 minute nap...")
                time.sleep(60)
                continue

            price_sats = top_bid.amount
            contribution_amount = auction.item.seller.get_contribution_amount(price_sats * quantity)
            if auction.campaign_id:
                contribution_amount = 0

            if contribution_amount != 0:
                response = get_lnd_client().add_invoice(value=contribution_amount, expiry=app.config['LND_CONTRIBUTION_INVOICE_EXPIRY_AUCTION'])
                contribution_payment_request = response.payment_request
            else:
                contribution_payment_request = None

            sale = m.Sale(item_id=auction.item_id, auction_id=auction.id,
                buyer_id=top_bid.buyer_id,
                address=address,
                price_usd=sats2usd(price_sats, btc2usd),
                price=price_sats,
                shipping_domestic=usd2sats(auction.item.shipping_domestic_usd, btc2usd),
                shipping_worldwide=usd2sats(auction.item.shipping_worldwide_usd, btc2usd),
                quantity=quantity,
                amount=(price_sats * quantity) - contribution_amount,
                contribution_amount=contribution_amount,
                contribution_payment_request=contribution_payment_request)
            if not contribution_payment_request:
                sale.state = m.SaleState.CONTRIBUTION_SETTLED.value
            db.session.add(sale)

            try:
                db.session.commit()
            except IntegrityError:
                # this should never happen...
                app.logger.error(f"Address already in use. Will retry next time. {auction.id=}")
                continue

            m.Message.create_and_send('AUCTION_HAS_WINNER', user=sale.item.seller, auction=sale.auction, buyer=sale.buyer)
            m.Message.create_and_send('AUCTION_WON', user=sale.buyer, auction=sale.auction)

        if app.config['ENV'] == 'test':
            time.sleep(1)
        else:
            time.sleep(5)

@app.cli.command("settle-lnd-payments")
@with_appcontext
def settle_lnd_payments():
    app.logger.setLevel(getattr(logging, LOG_LEVEL))
    signal.signal(signal.SIGTERM, lambda _, __: sys.exit(0))

    while True:
        lnd = get_lnd_client()
        last_settle_index = int(db.session.query(m.State).filter_by(key=m.State.LAST_SETTLE_INDEX).first().value)
        app.logger.info(f"Subscribing to LND invoices using {type(lnd)}. {last_settle_index=}")
        try:
            for invoice in lnd.subscribe_invoices(settle_index=last_settle_index):
                if invoice.state == lndgrpc.client.ln.SETTLED and invoice.settle_index > last_settle_index:
                    found_invoice = False
                    bid = db.session.query(m.Bid).filter_by(payment_request=invoice.payment_request).first()
                    if bid:
                        found_invoice = True
                        bid.settled_at = datetime.utcnow()
                        bid.auction.extend()
                        app.logger.info(f"Settled bid: {bid.id=} {bid.amount=}.")
                    else:
                        sale = db.session.query(m.Sale).filter_by(contribution_payment_request=invoice.payment_request).first()
                        if sale:
                            found_invoice = True
                            if sale.state not in [m.SaleState.TX_DETECTED.value, m.SaleState.TX_CONFIRMED.value]:
                                # NB: in theory, the contribution should always settle before we get a TX, but you never know...
                                # it could be that this process, or the lightning node, went down
                                # and the user managed to get an on-chain TX in first.
                                # we certainly don't want to change the state in that case!
                                sale.state = m.SaleState.CONTRIBUTION_SETTLED.value
                            sale.contribution_settled_at = datetime.utcnow()
                            app.logger.info(f"Settled sale contribution: {sale.id=} {sale.contribution_amount=}.")
                    if found_invoice:
                        last_settle_index = invoice.settle_index
                        state = db.session.query(m.State).filter_by(key=m.State.LAST_SETTLE_INDEX).first()
                        state.value = str(last_settle_index)
                        db.session.commit()
        except:
            app.logger.exception("Error while processing LND invoices. Will roll back and retry.")
            db.session.rollback()
        else:
            app.logger.warning("Disconnected from LND. Sleep, then retry...")

        if app.config['ENV'] == 'test':
            time.sleep(1)
        else:
            time.sleep(10)

@app.cli.command("settle-btc-payments")
@with_appcontext
def settle_btc_payments():
    app.logger.setLevel(getattr(logging, LOG_LEVEL))
    signal.signal(signal.SIGTERM, lambda _, __: sys.exit(0))

    btc = get_btc_client()

    app.logger.info(f"Starting to settle BTC payments using {type(btc)}...")

    while True:
        try:
            for sale in db.session.query(m.Sale).filter((m.Sale.settled_at == None) & (m.Sale.expired_at == None)):
                if app.config['ENV'] == 'test' and sale.requested_at >= (datetime.utcnow() - timedelta(seconds=3)):
                    # in test mode, don't settle the sales right away, to give them time to the contribution to settle first
                    app.logger.warning("Waiting...")
                    continue
                try:
                    funding_txs = btc.get_funding_txs(sale.address)
                except MempoolSpaceError as e:
                    app.logger.warning(str(e) + f" {sale.address=} Taking a 1 minute nap...")
                    time.sleep(60)
                    continue
                for tx in funding_txs:
                    if sale.txid and not sale.settled_at:
                        if tx['confirmed'] and (tx['txid'] == sale.txid or tx['value'] == sale.tx_value):
                            if tx['txid'] != sale.txid:
                                # this can actually happen if the buyer replaces the tx in the mempool with a new tx,
                                # for example in order to change the fee
                                app.logger.info(f"Transaction txid={tx['txid']} differs from original txid={sale.txid} matching {sale.id=} but we still accept it.")
                                sale.txid = tx['txid']
                            app.logger.info(f"Confirmed transaction txid={tx['txid']} matching {sale.id=}.")
                            sale.state = m.SaleState.TX_CONFIRMED.value
                            sale.settled_at = datetime.utcnow()
                            db.session.commit()
                            m.Message.create_and_send('TRANSACTION_CONFIRMED', user=sale.buyer, sale_id=sale.id, txid=tx['txid'])
                            break
                    elif not sale.txid:
                        if tx['value'] >= sale.amount:
                            app.logger.info(f"Found transaction txid={tx['txid']} confirmed={tx['confirmed']} matching {sale.id=}.")
                            sale.txid = tx['txid']
                            sale.tx_value = tx['value']
                            sale.state = m.SaleState.TX_DETECTED.value
                            if sale.is_badge_sale:
                                for_campaign = sale.campaign.key if sale.campaign_id else None
                                if not m.UserBadge.query.filter_by(user_id=sale.buyer_id, badge=sale.desired_badge, icon=for_campaign).first():
                                    app.logger.info(f"Sale {sale.id} awards badge {sale.desired_badge} with icon={for_campaign} to user {sale.buyer_id}.")
                                    db.session.add(m.UserBadge(user_id=sale.buyer_id, badge=sale.desired_badge, icon=for_campaign))
                                # awarding the "default icon" version of the badge in addition to the campaign version
                                icon = app.config['BADGE_DEFAULT_ICON']
                                if not m.UserBadge.query.filter_by(user_id=sale.buyer_id, badge=sale.desired_badge, icon=icon).first():
                                    app.logger.info(f"Sale {sale.id} awards badge {sale.desired_badge} with default icon to user {sale.buyer_id}.")
                                    db.session.add(m.UserBadge(user_id=sale.buyer_id, badge=sale.desired_badge, icon=icon))
                            if tx['confirmed']:
                                sale.state = m.SaleState.TX_CONFIRMED.value
                                sale.settled_at = datetime.utcnow()
                            db.session.commit()
                            m.Message.create_and_send('TRANSACTION_FOUND', user=sale.buyer, sale_id=sale.id, txid=tx['txid'], confirmed=tx['confirmed'])
                            break
                        else:
                            app.logger.warning(f"Found unexpected transaction when trying to settle {sale.id=}: {sale.amount=} {sale.shipping_domestic=} {sale.shipping_worldwide=} vs {tx['value']=}.")
                else:
                    if sale.requested_at < datetime.utcnow() - timedelta(minutes=sale.timeout_minutes):
                        app.logger.warning(f"Sale too old. Marking as expired. {sale.id=}")
                        sale.state = m.SaleState.EXPIRED.value
                        sale.expired_at = datetime.utcnow()
                        if sale.is_auction_sale:
                            # expired auction sales will give the next bidder the chance to buy the item
                            sale.auction.has_winner = None
                        if sale.is_listing_sale:
                            # expired listing sales increment the stock with the quantity that was decremented when the sale process was initiated
                            listing = db.session.query(m.Listing).filter_by(id=sale.listing_id).first()
                            listing.available_quantity += sale.quantity
                        db.session.commit()

                        # NB: we send messages after the final commit
                        # because sending messages performa extra commits!
                        if sale.is_auction_sale:
                            m.Message.create_and_send('SALE_EXPIRED', user=sale.item.seller, auction=sale.auction, buyer=sale.buyer)
                            m.Message.create_and_send('PURCHASE_EXPIRED', user=sale.buyer, auction=sale.auction)
        except:
            app.logger.exception("Error while settling BTC payments. Will roll back and retry.")
            db.session.rollback()

        if app.config['ENV'] == 'test':
            time.sleep(1)
        else:
            time.sleep(10)

@app.cli.command("process-notifications")
@with_appcontext
def process_notifications():
    app.logger.setLevel(getattr(logging, LOG_LEVEL))
    signal.signal(signal.SIGTERM, lambda _, __: sys.exit(0))

    # NB: this is used only as an optimization
    # The actual way of making sure we don't send the same notification twice is the database, namely the UNIQUE constraint on messages (user_id, key).
    # We store this list of sent notifications in memory so we can quickly skip duplicates and not even try to execute the INSERT query.
    # However, if this process is restarted, this list will be lost, so we will attempt to send (some of) the same notifications again.
    # That is when the database will save us as it will simply raise an integrity error.
    sent_notifications = set()

    while True:
        processing_started = datetime.utcnow()

        state = db.session.query(m.State).filter_by(key=m.State.LAST_PROCESSED_NOTIFICATIONS).one_or_none()
        if not state:
            # First time we ever run this process, there's not much to do,
            # as we don't want to send notifications for every event that happened in the past!
            state = m.State(key=m.State.LAST_PROCESSED_NOTIFICATIONS, value=str(int(processing_started.timestamp())))
            db.session.add(state)
            db.session.commit()
            time.sleep(1)
            continue

        last_processed_notifications = datetime.fromtimestamp(int(state.value))

        total_bids = 0
        total_auctions = 0
        start_time = time.time()

        # NB: we load 1) all (new) bids (since last run)
        # and 2) all auctions that are going to end in the next 10 minutes (or ended since the last run minus 10 minutes).
        # This ensures that notifications to be sent for new bids or for any auction ending soon or that just ended will be processed.
        # If we want (for example) notifications for newly created auctions (regardless of end date) we would have to load auctions based on created_at.
        for bid_or_auction in chain(
            db.session.query(m.Bid).filter(m.Bid.settled_at > last_processed_notifications), # TODO: select related auctions to optimize?
            db.session.query(m.Auction).filter((m.Auction.end_date <= (datetime.utcnow() + timedelta(minutes=10))) & (m.Auction.end_date > (last_processed_notifications - timedelta(minutes=10))))
        ):
            match bid_or_auction:
                case m.Bid():
                    bid = bid_or_auction
                    auction = bid.auction
                    total_bids += 1
                    app.logger.debug(f"Processing bid {bid.id=}.")
                case m.Auction():
                    bid = None
                    auction = bid_or_auction
                    total_auctions += 1
                    app.logger.debug(f"Processing auction {auction.id=}.")

            # this could be further optimized by caching the users following the running auctions in memory,
            # but we would need a way to invalidate/update the cache on follow/unfollow
            following_user_ids = [ua.user_id for ua in db.session.query(m.UserAuction).filter_by(auction_id=auction.id, following=True).all()]
            following_users = {u.id: u for u in db.session.query(m.User).filter(m.User.id.in_(following_user_ids)).all()}

            # notification settings for the users following the auction - could also be cached, with the same caveat as above
            user_notifications = {(un.user_id, un.notification_type): un for un in db.session.query(m.UserNotification).filter(m.UserNotification.user_id.in_(following_user_ids)).all()}

            for notification_type, notification in m.NOTIFICATION_TYPES.items():
                if notification_type not in m.BACKGROUND_PROCESS_NOTIFICATION_TYPES:
                    continue
                for user in following_users.values():
                    if (user.id, notification_type) in user_notifications:
                        action = user_notifications[(user.id, notification_type)].action
                    else:
                        action = notification.default_action

                    message_args = notification.get_message_args(user=user, auction=auction, bid=bid)
                    if not message_args:
                        # notification type does not apply in this case
                        continue

                    if (user.id, message_args['key']) in sent_notifications:
                        # already sent - don't even bother trying again (will fail anyway with IntegrityError)!
                        continue

                    # insert before actually trying to send anything to ensure uniqueness
                    message = m.Message(**message_args)
                    db.session.add(message)

                    try:
                        db.session.commit()
                    except IntegrityError:
                        app.logger.info(f"Duplicate message send attempt: {message_args['key']=} {message_args['user_id']=}!")
                        db.session.rollback()
                        # the message already exists for this user
                        # see the comment on sent_notifications above for details
                        continue

                    app.logger.info(f"Executing {action=} for {user.id=}!")
                    if m.NOTIFICATION_ACTIONS[action].execute(user, message):
                        app.logger.info(f"Notified {user.id=} with {action=}!")
                        message.notified_via = action
                    else:
                        pass
                        # db.session.delete(message)
                        # Probably better to keep the Message in the DB if sending failed,
                        # since notifications are supposed to be real time sort-of,
                        # so if the delivery failed we better don't try to send it later anyway!

                    sent_notifications.add((user.id, message_args['key']))
                    db.session.commit()

        state = db.session.query(m.State).filter_by(key=m.State.LAST_PROCESSED_NOTIFICATIONS).first()
        state.value = str(int(processing_started.timestamp()))
        db.session.commit()

        total_seconds = time.time() - start_time

        if total_bids != 0:
            app.logger.info(f"Processed {total_bids=} and {total_auctions=} in {total_seconds=}.")

        time.sleep(1)

@app.cli.command("set-campaign-banner")
@click.argument("key", type=click.STRING)
@click.argument("filename", type=click.STRING)
@with_appcontext
def set_campaign_banner(key, filename):
    from utils import store_image

    campaign = db.session.query(m.Campaign).filter_by(key=key).one_or_none()
    if not campaign:
        app.logger.error("Campaign not found.")
        return

    if not os.path.exists(filename):
        app.logger.error("File not found.")
        return

    with open(filename, "rb") as f:
        data = f.read()

    url, _ = store_image(get_s3(), f"campaign_{key}_banner", True, filename, data)
    if not url:
        app.logger.error("Error saving banner.")
        return

    campaign.banner_url = url
    db.session.commit()

def get_token_from_request():
    return request.headers.get('X-Access-Token')

def get_user_from_token(token):
    if not token:
        return None

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    except Exception:
        return None

    if 'user_id' in data:
        q = m.User.id == data['user_id']
    else:
        # NB: we started storing the user id in the JWT token recently,
        # but we don't want to forcefully log out all users that have old tokens,
        # so keep this code around for now, but we should get rid of it later!
        if 'user_key' in data:
            q = m.User.lnauth_key == data['user_key']
        elif 'user_lnauth_key' in data:
            q = m.User.lnauth_key == data['user_lnauth_key']
        elif 'user_nostr_public_key' in data:
            q = m.User.nostr_public_key == data['user_nostr_public_key']
        else:
            return None

    return m.User.query.filter(q).first()

def user_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'success': False, 'message': "Missing token."}), 401
        user = get_user_from_token(token)
        if not user:
            return jsonify({'success': False, 'message': "Invalid token."}), 401
        return f(user, *args, **kwargs)
    return decorator

class MockLNDClient:
    class InvoiceResponse:
        def __init__(self, payment_request=None, state=None, settle_index=None):
            if payment_request:
                self.payment_request = payment_request
            else:
                self.payment_request = "MOCK_" + ''.join(random.choice(string.ascii_lowercase) for i in range(8))
            self.state = state
            self.settle_index = settle_index

    def add_invoice(self, value, **_):
        return MockLNDClient.InvoiceResponse()

    def subscribe_invoices(self, **_):
        last_settle_index = int(db.session.query(m.State).filter_by(key=m.State.LAST_SETTLE_INDEX).first().value)
        while True:
            time.sleep(3)
            for unsettled_bid in db.session.query(m.Bid).filter(m.Bid.settled_at == None):
                if unsettled_bid.requested_at > datetime.utcnow() - timedelta(seconds=1):
                    # give it at least a second in test mode
                    continue
                last_settle_index += 1
                yield MockLNDClient.InvoiceResponse(unsettled_bid.payment_request, lndgrpc.client.ln.SETTLED, last_settle_index)
            for unsettled_sale_contribution in db.session.query(m.Sale).filter(m.Sale.contribution_settled_at == None):
                if unsettled_sale_contribution.requested_at > datetime.utcnow() - timedelta(seconds=1):
                    # give it at least a second in test mode
                    continue
                last_settle_index += 1
                yield MockLNDClient.InvoiceResponse(unsettled_sale_contribution.contribution_payment_request, lndgrpc.client.ln.SETTLED, last_settle_index)

def get_lnd_client():
    if app.config['MOCK_LND']:
        return MockLNDClient()
    else:
        return lndgrpc.LNDClient(app.config['LND_GRPC'], macaroon_filepath=app.config['LND_MACAROON'], cert_filepath=app.config['LND_TLS_CERT'])

class MockBTCClient:
    def get_funding_txs(self, addr):
        sale = db.session.query(m.Sale).filter(m.Sale.address == addr).first()
        if sale:
            confirmed = sale.txid is not None
            block_time = datetime.utcnow() - timedelta(seconds=5) if confirmed else None
            return [{'txid': 'MOCK_TXID', 'value': sale.amount + sale.shipping_domestic + int(sale.shipping_domestic / 100), 'confirmed': confirmed, 'block_time': block_time}]
        else:
            return []

class MempoolSpaceError(Exception):
    def __str__(self):
        return "Error reading from mempool API!"

class MempoolSpaceBTCClient:
    def get_funding_txs(self, addr):
        if addr.startswith("OLD_"): # not a real address, but a placeholder we used for sales from before we started accepting on-chain payments
            return []

        try:
            response_json = requests.get(f"https://mempool.space/api/address/{addr}/txs").json()
        except JSONDecodeError as e:
            raise MempoolSpaceError() from e

        txs = []
        for tx in response_json:
            vout_for_addr = [vo for vo in tx['vout'] if vo.get('scriptpubkey_address') == addr]
            if len(vout_for_addr) > 1:
                app.logger.warning("Multiple outputs for same address? Strange...")
            value = sum(vo['value'] for vo in vout_for_addr)
            txs.append({
                'txid': tx['txid'],
                'value': value,
                'confirmed': tx['status']['confirmed'],
                'block_time': datetime.fromtimestamp(tx['status']['block_time']) if tx['status']['confirmed'] else None,
            })

        return txs

def get_btc_client():
    if app.config['MOCK_BTC']:
        return MockBTCClient()
    else:
        return MempoolSpaceBTCClient()

class MockTwitter:
    class MockKey:
        def __eq__(self, other):
            return True

    def __init__(self, **__):
        pass

    def get_verification_phrase(self, user):
        return "i am me"

    def get_user(self, username):
        if app.config['ENV'] == 'test':
            # hammer staging rather than picsum when running tests
            random_image_small = random_image_large = "https://staging.plebeian.market/images/logo.jpg"
        else:
            random_image_small = "https://picsum.photos/200"
            random_image_large = "https://picsum.photos/1500"
        return {
            'id': "MOCK_USER_ID",
            'profile_image_url': random_image_small,
            'pinned_tweet_id': "MOCK_PINNED_TWEET",
            'created_at': datetime.now() - timedelta(days=(app.config['TWITTER_USER_MIN_AGE_DAYS'] + 1)),
        }

    def get_sale_tweets(self, user_id, entity_endpoint):
        if not user_id.startswith('MOCK_USER'):
            return None
        time.sleep(5) # deliberately slow this down, so we can find possible issues in the UI
        if app.config['ENV'] == 'test':
            # hammer staging rather than picsum when running tests
            random_image = "https://staging.plebeian.market/images/logo.jpg"
        else:
            random_image = "https://picsum.photos/1024"
        return [{
            'id': "MOCK_TWEET_ID",
            'text': "Hello Mocked Tweet",
            'created_at': datetime.now().isoformat(),
            'auction_key': MockTwitter.MockKey(),
            'photos': [
                {'media_key': f"MOCK_PHOTO_{i}", 'url': random_image} for i in range(4)
            ]
        }]

    def send_dm(self, user_id, body):
        app.logger.info(f"Twitter DM: {body}!")
        # NB: we are not actually testing that sending Twitter DMs works,
        # but we are testing the notifications mechanism - so assume the DM went through
        return True

class Twitter:
    BASE_URL = "https://api.twitter.com"
    URL_PREFIXES = ["http://plebeian.market/%s/", "https://plebeian.market/%s/", "http://staging.plebeian.market/%s/", "https://staging.plebeian.market/%s/"]

    def __init__(self, api_key, api_key_secret, access_token, access_token_secret):
        self.session = OAuth1Session(api_key, api_key_secret, access_token, access_token_secret)

    def get_verification_phrase(self, user):
        return user.twitter_verification_phrase

    def get(self, path, params=None):
        if params is None:
            params = {}
        response = self.session.get(f"{Twitter.BASE_URL}{path}", params=params)
        if response.status_code == 200:
            return response.json()

    def post(self, path, params_json):
        response = self.session.post(f"{Twitter.BASE_URL}{path}", json=params_json)
        if response.status_code == 200:
            return response.json()
        else:
            app.logger.error(f"Error when POSTing to Twitter -> {path}: {response.status_code=} {response.text=}")
            return False

    def get_user(self, username):
        response_json = self.get(f"/2/users/by/username/{username}",
            params={
                'user.fields': "location,name,profile_image_url,pinned_tweet_id,created_at",
            })

        if not response_json or response_json.get('errors'):
            return

        twitter_user = response_json['data']

        if '_normal' in twitter_user['profile_image_url']:
            # pick high-res picture
            # see https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/user-profile-images-and-banners
            twitter_user['profile_image_url'] = twitter_user['profile_image_url'].replace('_normal', '')

        twitter_user['created_at'] = dateutil.parser.isoparse(twitter_user['created_at']).replace(tzinfo=None)

        return twitter_user

    def get_sale_tweets(self, user_id, entity_endpoint):
        response_json = self.get(f"/2/users/{user_id}/tweets",
            params={
                'max_results': 100,
                'expansions': "attachments.media_keys",
                'media.fields': "url",
                'tweet.fields': "id,text,entities,created_at"})

        if not response_json or response_json.get('errors'):
            return []

        auction_tweets = []
        for tweet in response_json.get('data', []):
            auction_key = None
            for url in tweet.get('entities', {}).get('urls', []):
                for p in Twitter.URL_PREFIXES:
                    p = p % entity_endpoint
                    if url['expanded_url'].startswith(p):
                        auction_key = url['expanded_url'].removeprefix(p)
                        break

            if auction_key:
                media_keys = tweet.get('attachments', {}).get('media_keys', [])
                auction_tweets.append({
                    'id': tweet['id'],
                    'text': tweet['text'],
                    'created_at': tweet['created_at'],
                    'auction_key': auction_key,
                    'photos': [
                        m for m in response_json['includes']['media']
                            if m['media_key'] in media_keys and m['type'].lower() in ('animated_gif', 'photo')
                    ],
                })

        return auction_tweets

    def send_dm(self, user_id, body):
        response_json = self.post(f"/2/dm_conversations/with/{user_id}/messages", params_json={'text': body})
        return bool(response_json)

def get_twitter():
    if app.config['MOCK_TWITTER']:
        return MockTwitter()
    else:
        with open(app.config['TWITTER_SECRETS']) as f:
            twitter_secrets = json.load(f)
        api_key = twitter_secrets['API_KEY']
        api_key_secret = twitter_secrets['API_KEY_SECRET']
        access_token = twitter_secrets['ACCESS_TOKEN']
        access_token_secret = twitter_secrets['ACCESS_TOKEN_SECRET']
        return Twitter(api_key, api_key_secret, access_token, access_token_secret)

class MockNostrClient:
    class MockKey:
        def __eq__(self, other):
            return True

    def __init__(self, **__):
        pass

    def get_auth_verification_phrase(self, auth):
        return "identifying as myself"

    def get_verification_phrase(self, user):
        return "i am me"

    def send_dm(self, recipient_public_key, body):
        app.logger.info(f"Nostr DM for {recipient_public_key}: {body}!")
        return True

    def publish_stall(self, *args, **kwargs):
        app.logger.info(f"Nostr Stall: {args=} {kwargs=}")
        return True

    def publish_product(self, *args, **kwargs):
        app.logger.info(f"Nostr Product: {args=} {kwargs=}")
        return True

class NostrClient:
    def __init__(self, private_key, relays):
        self.private_key = private_key
        self.relay_manager = RelayManager()
        for relay in relays:
            self.relay_manager.add_relay(relay)

    def get_auth_verification_phrase(self, auth):
        return auth.verification_phrase

    def get_verification_phrase(self, user):
        return user.nostr_verification_phrase

    def send_dm(self, recipient_public_key, body):
        try:
            dm = EncryptedDirectMessage(recipient_pubkey=recipient_public_key, cleartext_content=body)
            self.private_key.sign_event(dm)
            self.relay_manager.publish_event(dm)
            return True
        except:
            app.logger.exception("Error while sending Nostr DM.")
            return False

    def publish_stall(self, id, name, description, currency, shipping_from, shipping_domestic_usd, shipping_worldwide_usd):
        try:
            stall_json = {
                'id': id,
                'name': name,
                'description': description,
                'currency': currency,
                'shipping': [
                    {
                        'id': hashlib.sha256(shipping_from.encode('utf-8')).hexdigest(),
                        'cost': shipping_domestic_usd,
                        'countries': [shipping_from],
                    },
                    {
                        'id': 'WORLD',
                        'cost': shipping_worldwide_usd,
                        'countries': ["Worldwide"],
                    },
                ]}
            event = Event(kind=30017, content=json.dumps(stall_json))
            self.private_key.sign_event(event)
            self.relay_manager.publish_event(event)
            return True
        except:
            app.logger.exception("Error while publishing Nostr stall.")
            return False

    def publish_product(self, id, stall_id, name, description, images, currency, price, quantity):
        try:
            product_json = {
                'id': id,
                'stall_id': stall_id,
                'name': name,
                'description': description,
                'images': images,
                'currency': currency,
                'price': price,
                'quantity': quantity
            }
            event = Event(kind=30018, content=json.dumps(product_json))
            self.private_key.sign_event(event)
            app.logger.debug(f"Publishing to Nostr: relays={self.relay_manager.relays.keys()} {event=}.")
            self.relay_manager.publish_event(event)
            return True
        except:
            app.logger.exception("Error while publishing Nostr product.")
            return False

def get_nostr_client(user):
    if app.config['MOCK_NOSTR']:
        return MockNostrClient()
    else:
        if user is None:
            with open(app.config['NOSTR_SECRETS']) as f:
                private_key = PrivateKey.from_nsec(json.load(f)['NSEC'])
            relays = app.config['DEFAULT_NOSTR_RELAYS']
        else:
            private_key = PrivateKey(bytes.fromhex(user.stall_private_key))
            relays = [r['url'] for r in user.get_relays()]
        return NostrClient(private_key, relays)

class MockS3:
    def get_url_prefix(self):
        return app.config['API_BASE_URL'] + "/mock-s3-files/"

    def get_filename_prefix(self):
        return ""

    def upload(self, data, filename):
        filename_with_prefix = self.get_filename_prefix() + filename
        app.logger.info(f"Upload {filename_with_prefix} to MockS3!")
        with open(f"/tmp/{filename_with_prefix}", "wb") as f:
            # basically store the content under /tmp to be used by the /mock-s3-files/ route later
            f.write(data)

class S3:
    def __init__(self, endpoint_url, key_id, application_key):
        self.s3 = boto3.resource(service_name='s3', endpoint_url=endpoint_url, aws_access_key_id=key_id, aws_secret_access_key=application_key, config=Config(signature_version='s3v4'))

    def get_url_prefix(self):
        return app.config['S3_URL_PREFIX']

    def get_filename_prefix(self):
        return app.config['S3_FILENAME_PREFIX']

    def upload(self, data, filename):
        self.s3.Bucket(app.config['S3_BUCKET']).upload_fileobj(io.BytesIO(data), self.get_filename_prefix() + filename)

def get_s3():
    if app.config['MOCK_S3']:
        return MockS3()
    else:
        with open(app.config['S3_SECRETS']) as f:
            s3_secrets = json.load(f)
        return S3(app.config['S3_ENDPOINT_URL'], s3_secrets['KEY_ID'], s3_secrets['APPLICATION_KEY'])

if __name__ == '__main__':
    import lnurl
    try:
        lnurl.encode(app.config['API_BASE_URL'])
    except lnurl.exceptions.InvalidUrl:
        # HACK: allow URLs with http:// and no TLD in development mode (http://localhost)
        from pydantic import AnyHttpUrl
        class ClearnetUrl(AnyHttpUrl):
            pass
        app.logger.warning("Patching lnurl.types.ClearnetUrl!")
        lnurl.types.ClearnetUrl = ClearnetUrl
        lnurl.encode(app.config['API_BASE_URL']) # try parsing again to check that the patch worked

    @app.route("/mock-s3-files/<string:filename>", methods=['GET'])
    def mock_s3(filename):
        app.logger.info(f"Fetch {filename} from MockS3!")
        with open(f"/tmp/{filename}", "rb") as f:
            data = f.read()
            return send_file(io.BytesIO(data), mimetype=magic.from_buffer(data, mime=True))

    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


def _store_lnauth_key(lnkey):
    """Grabs the latest LnAuth entry and stores `lnkey` in the field"""
    ln = m.LnAuth.query.order_by(desc(m.LnAuth.created_at)).first()
    ln.key = lnkey
    db.session.commit()


@app.cli.command("lnauth")
@click.argument("lnkey", type=click.STRING)
@with_appcontext
def store_lnauth_key(lnkey):
    """
    For dev env - simplifies passing by the ln-auth system
    Creates a ln auth entry with api key
    :param lnkey: str
    """
    click.echo(f'Setting latest LnAuth key: {lnkey}')
    _store_lnauth_key(lnkey)
