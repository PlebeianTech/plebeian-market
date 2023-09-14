import base64
import boto3
from botocore.config import Config
import click
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_file
from flask.cli import with_appcontext
from flask_mail import Message
from flask_migrate import Migrate
from functools import wraps
import hashlib
import io
import json
import jwt
import logging
from logging.config import dictConfig
import magic
from nostr.event import Event, EncryptedDirectMessage
from nostr.key import PrivateKey
import os
import requests
from requests.exceptions import JSONDecodeError
import signal
from sqlalchemy import desc
import sys
import time
import uuid

from extensions import cors, db, mail
from utils import hash_create

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
    mail.init_app(app)
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
        for auction in db.session.query(m.Auction).filter((m.Auction.end_date <= datetime.utcnow()) & (m.Auction.has_winner == None)):
            app.logger.info(f"Looking at {auction.id=}...")

            top_bid = auction.get_top_bid()

            while top_bid and db.session.query(m.Order).filter_by(buyer_public_key=top_bid.buyer_nostr_public_key).filter(m.Order.expired_at != None) \
            .join(m.OrderItem, m.OrderItem.order_id == m.Order.id).filter(m.OrderItem.auction_id == auction.id).first():
                app.logger.info(f"Skipping bidder {top_bid.buyer_nostr_public_key} with expired order for {auction.id=} and picking the next one!")
                top_bid = auction.get_top_bid(below=top_bid.amount)

            if not top_bid or not auction.reserve_bid_reached:
                app.logger.info(f"Auction {auction.id=} has no winner!")
                auction.has_winner = False
                auction.winning_bid_id = None
                db.session.commit()
                continue

            app.logger.info(f"Auction {auction.id=} has a winner: pubkey={top_bid.buyer_nostr_public_key}!")
            auction.has_winner = True
            auction.winning_bid_id = top_bid.id

            if top_bid.buyer_nostr_public_key:
                merchant = auction.item.seller
                if merchant.wallet:
                    try:
                        on_chain_address = merchant.get_new_address()
                    except m.AddressGenerationError:
                        app.logger.exception("Error while generating address.")
                        continue
                    except MempoolSpaceError:
                        app.logger.exception("Error while checking mempool.")
                        continue
                else:
                    on_chain_address = None
                lightning_address = merchant.lightning_address

                order_uuid = str(uuid.uuid4())

                birdwatcher = get_birdwatcher()

                if not birdwatcher.publish_bid_status(auction, top_bid.nostr_event_id, 'winner', extra_tags=[['p', top_bid.buyer_nostr_public_key]]):
                    continue

                dm_event_id = birdwatcher.send_dm(auction.item.seller.parse_merchant_private_key(), top_bid.buyer_nostr_public_key,
                    json.dumps({'id': order_uuid, 'type': 10, 'items': [{'product_id': str(auction.uuid), 'quantity': 1}]}))
                if not dm_event_id:
                    continue

                order = m.Order(
                    uuid=order_uuid,
                    seller_id=auction.item.seller_id,
                    buyer_public_key=top_bid.buyer_nostr_public_key,
                    requested_at=datetime.utcnow(),
                    on_chain_address=on_chain_address,
                    lightning_address=lightning_address,
                    event_id=dm_event_id)
                db.session.add(order)
                db.session.commit()

                order_item = m.OrderItem(order_id=order.id, item_id=auction.item_id, auction_id=auction.id, quantity=1)
                db.session.add(order_item)

            db.session.commit()

        if app.config['ENV'] == 'test':
            time.sleep(1)
        else:
            time.sleep(5)

@app.cli.command("settle-btc-payments")
@with_appcontext
def settle_btc_payments():
    app.logger.setLevel(getattr(logging, LOG_LEVEL))
    signal.signal(signal.SIGTERM, lambda _, __: sys.exit(0))

    btc = get_btc_client()

    app.logger.info(f"Starting to settle BTC payments using {type(btc)}...")

    while True:
        try:
            active_filter = (m.Order.paid_at == None) & (m.Order.expired_at == None) & (m.Order.canceled_at == None)
            for order in db.session.query(m.Order).filter((m.Order.on_chain_address != None) & active_filter):
                try:
                    funding_txs = btc.get_funding_txs(order.on_chain_address)
                except MempoolSpaceError as e:
                    app.logger.warning(str(e) + f" {order.on_chain_address=} Taking a 1 minute nap...")
                    time.sleep(60)
                    continue
                birdwatcher = get_birdwatcher()
                for tx in funding_txs:
                    if order.txid and not order.tx_confirmed:
                        if tx['confirmed'] and (tx['txid'] == order.txid or tx['value'] == order.tx_value):
                            if tx['txid'] != order.txid:
                                # this can happen in case of RBF
                                app.logger.info(f"Transaction txid={tx['txid']} differs from original txid={order.txid} matching {order.id=} but we still accept it.")
                                order.txid = tx['txid']
                            app.logger.info(f"Confirmed transaction txid={tx['txid']} matching {order.id=}.")
                            order.tx_confirmed = True
                            order.paid_at = datetime.utcnow()
                            if not birdwatcher.send_dm(order.seller.parse_merchant_private_key(), order.buyer_public_key,
                                json.dumps({'id': order.uuid, 'type': 2, 'paid': True, 'shipped': False, 'message': f"Payment confirmed. TxID: {order.txid}"})):
                                continue
                            db.session.commit()
                            break
                    elif not order.txid:
                        if tx['value'] >= order.total:
                            app.logger.info(f"Found transaction txid={tx['txid']} confirmed={tx['confirmed']} matching {order.id=}.")
                            order.txid = tx['txid']
                            order.tx_value = tx['value']
                            if tx['confirmed']:
                                order.tx_confirmed = True
                                order.paid_at = datetime.utcnow()
                                if not birdwatcher.send_dm(order.seller.parse_merchant_private_key(), order.buyer_public_key,
                                    json.dumps({'id': order.uuid, 'type': 2, 'paid': True, 'shipped': False, 'message': f"Payment confirmed. TxID: {order.txid}"})):
                                    continue
                            else:
                                message = f"Found transaction. Waiting for confirmation. TxID: {order.txid}"
                                if not birdwatcher.send_dm(order.seller.parse_merchant_private_key(), order.buyer_public_key,
                                    json.dumps({'id': order.uuid, 'type': 2, 'paid': False, 'shipped': False, 'message': message})):
                                    continue
                            db.session.commit()
                            break
                        else:
                            app.logger.warning(f"Found unexpected transaction when trying to settle {order.id=}: {order.total=} vs {tx['value']=}.")
                else:
                    if order.requested_at < datetime.utcnow() - timedelta(minutes=order.timeout_minutes):
                        app.logger.warning(f"Order too old. Marking as expired. {order.id=}")
                        order.expired_at = datetime.utcnow()
                        for order_item in db.session.query(m.OrderItem).filter_by(order_id=order.id):
                            # expired orders increment the stock with the quantity that was decremented when the order was created
                            # (for Listings, not for Auctions - auctions with expired orders are taken care of in finalize-auctions,
                            # where we detect the expired order and pick the next highest bidder as the new winner!)
                            if order_item.listing_id:
                                listing = db.session.query(m.Listing).filter_by(id=order_item.listing_id).first()
                                listing.available_quantity += order_item.quantity
                                birdwatcher.publish_product(listing) # TODO: what could we do here if this fails?
                        if not birdwatcher.send_dm(order.seller.parse_merchant_private_key(), order.buyer_public_key,
                            json.dumps({'id': order.uuid, 'type': 2, 'paid': False, 'shipped': False, 'message': "Order expired."})):
                            continue
                        db.session.commit()
                if order.paid_at and order.has_skin_in_the_game_badge():
                    birdwatcher = get_birdwatcher()
                    if not birdwatcher.publish_badge_award(app.config['BADGE_DEFINITION_SKIN_IN_THE_GAME']['badge_id'], order.buyer_public_key):
                        app.logger.error("Failed to publish Skin in the Game badge award!")
                    else:
                        app.logger.info(f"Awarded Skin in the Game badge for {order.buyer_public_key}!")
                        if not birdwatcher.send_dm(order.seller.parse_merchant_private_key(), order.buyer_public_key,
                            json.dumps({'id': order.uuid, 'type': 2, 'paid': True, 'shipped': True, 'message': "Skin in the Game badge awarded!"})):
                            app.logger.error("Error sending Nostr reply to the buyer.")
                        for pending_bid in m.Bid.query.filter_by(buyer_nostr_public_key=order.buyer_public_key, settled_at=None).all():
                            app.logger.info(f"Confirmed bid {pending_bid.id} after having acquired the Skin in the Game badge!")
                            pending_bid.settled_at = datetime.utcnow()
                            duration_extended = pending_bid.auction.extend()
                            birdwatcher.publish_bid_status(pending_bid.auction, pending_bid.nostr_event_id, 'accepted', duration_extended=duration_extended)
                            db.session.commit()
        except:
            app.logger.exception("Error while settling BTC payments. Will roll back and retry.")
            db.session.rollback()

        if app.config['ENV'] == 'test':
            time.sleep(1)
        else:
            time.sleep(10)

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

class MockBTCClient:
    def get_funding_txs(self, addr):
        order = db.session.query(m.Order).filter(m.Order.on_chain_address == addr).first()
        if order:
            confirmed = order.txid is not None
            block_time = datetime.utcnow() - timedelta(seconds=5) if confirmed else None
            return [{'txid': 'MOCK_TXID', 'value': order.total, 'confirmed': confirmed, 'block_time': block_time}]
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
            response_json = requests.get(f"https://mempool.space/{'testnet/' if addr.startswith('t') else ''}api/address/{addr}/txs").json()
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

class Birdwatcher:
    def __init__(self, base_url):
        self.base_url = base_url
        if app.config['MOCK_NOSTR']:
            # NB: in test mode we just use a random private key!
            self.site_admin_private_key = PrivateKey()
        else:
            with open(app.config['SITE_ADMIN_SECRETS']) as f:
                site_admin_secrets = json.load(f)
                self.site_admin_private_key = PrivateKey.from_nsec(site_admin_secrets['NSEC'])

    def query_metadata(self, public_key):
        response = requests.post(f"{self.base_url}/query", json={'metadata': True, 'authors': [public_key]})
        if response.status_code == 200:
            return response.json()
        else:
            app.logger.error(f"Error querying birdwatcher for {public_key} metadata!")
            return None

    def add_relay(self, relay_url):
        response = requests.post(f"{self.base_url}/relays", json={'url': relay_url})
        if response.status_code == 200:
            app.logger.info(f"Successfully POSTed relay {relay_url} to birdwatcher!")
            return True
        else:
            app.logger.error(f"Error POSTing relay {relay_url} to birdwatcher!")
            return False

    def post_event(self, event):
        event_json = json.loads(event.to_message())[1] # ugly as hell. maybe we should just completely get rid of this python-nostr library, it's been a pain in the ass!
        response = requests.post(f"{self.base_url}/events", json=event_json)
        if response.status_code == 200:
            app.logger.info(f"Successfully POSTed event {event.id} to birdwatcher: {event_json=}!")
            return True
        else:
            app.logger.error(f"Error POSTing event {event.id} to birdwatcher!")
            return False

    def send_dm(self, sender_private_key, recipient_public_key, body):
        try:
            dm = EncryptedDirectMessage(recipient_pubkey=recipient_public_key, cleartext_content=body)
            sender_private_key.sign_event(dm)
            if self.post_event(dm):
                return dm.id
        except:
            app.logger.exception(f"Error sending DM for {recipient_public_key} via birdwatcher!")

    def publish_stall(self, merchant):
        STALL_EVENT_KIND = 31017 if app.config['ENV'] == 'staging' else 30017
        stall_json = merchant.to_nostr_stall()
        try:
            event = Event(kind=STALL_EVENT_KIND, content=json.dumps(stall_json), tags=[['d', stall_json['id']]])
            merchant.parse_merchant_private_key().sign_event(event)
            if self.post_event(event):
                return event.id
        except:
            app.logger.exception(f"Error publishing stall for merchant {merchant.merchant_public_key} via birdwatcher!")

    def delete_stall(self, merchant):
        try:
            event = Event(kind=5, content=f"Stall \"{merchant.stall_name}\" deleted!", tags=[['e', merchant.stall_nostr_event_id]])
            merchant.parse_merchant_private_key().sign_event(event)
            if self.post_event(event):
                return event.id
        except:
            app.logger.exception(f"Error deleting stall for merchant {merchant.merchant_public_key} via birdwatcher!")

    def publish_product(self, entity, extra_media=None):
        product_json = entity.to_nostr(extra_media)
        try:
            event = Event(kind=entity.nostr_event_kind, content=json.dumps(product_json), tags=[['d', product_json['id']]])
            entity.item.seller.parse_merchant_private_key().sign_event(event)
            if self.post_event(event):
                return event.id
        except:
            app.logger.exception(f"Error publishing product for merchant {entity.item.seller.merchant_public_key} via birdwatcher!")

    def delete_product(self, entity):
        try:
            event = Event(kind=5, content=f"Item \"{entity.item.title}\" deleted!", tags=[['e', entity.nostr_event_id]])
            entity.item.seller.parse_merchant_private_key().sign_event(event)
            if self.post_event(event):
                return event.id
        except:
            app.logger.exception(f"Error deleting product for merchant {entity.item.seller.merchant_public_key} via birdwatcher!")

    def publish_bid_status(self, auction, bid_event_id, status, message=None, duration_extended=0, donation_stall_ids=None, extra_tags=None):
        BID_STATUS_EVENT_KIND = 2022 if app.config['ENV'] == 'staging' else 1022
        try:
            if extra_tags is None:
                extra_tags = []
            content_json = {'status': status}
            if message is not None:
                content_json['message'] = message
            if duration_extended != 0:
                content_json['duration_extended'] = duration_extended
            if donation_stall_ids is not None:
                content_json['donation_stall_ids'] = donation_stall_ids
            event = Event(kind=BID_STATUS_EVENT_KIND, content=json.dumps(content_json), tags=([['e', auction.nostr_event_id], ['e', bid_event_id]] + extra_tags))
            auction.item.seller.parse_merchant_private_key().sign_event(event)
            if self.post_event(event):
                return event.id
        except:
            app.logger.exception(f"Error publishing bid status for bid {bid_event_id} via birdwatcher!")

    def publish_badge_definition(self, badge_id, name, description, image_url):
        try:
            if app.config['ENV'] == 'staging':
                badge_id_tag = badge_id + "-staging"
                name_tag = name + " (staging)"
            else:
                badge_id_tag = badge_id
                name_tag = name
            event = Event(kind=30009, content="", tags=[['d', badge_id_tag], ['name', name_tag], ['description', description], ['image', image_url]])
            self.site_admin_private_key.sign_event(event)
            if self.post_event(event):
                return event.id
        except:
            app.logger.exception(f"Error publishing badge definition via birdwatcher!")

    def publish_badge_award(self, badge_id, pubkey):
        try:
            if app.config['ENV'] == 'staging':
                badge_id_tag = badge_id + "-staging"
            else:
                badge_id_tag = badge_id
            event = Event(kind=8, content="", tags=[['a', f"30009:{self.site_admin_private_key.public_key.hex()}:{badge_id_tag}"], ['p', pubkey]])
            self.site_admin_private_key.sign_event(event)
            if self.post_event(event):
                return event.id
        except:
            app.logger.exception(f"Error publishing badge award via birdwatcher!")

class MockingBirdwatcher:
    def query_metadata(self, _public_key):
        return {'events': {}, 'verified_identities': []}

    def add_relay(self, relay_url):
        app.logger.info(f"add_relay url={relay_url}")
        return True

    def send_dm(self, sender_private_key, recipient_public_key, body):
        app.logger.info(f"from={sender_private_key.hex()} to={recipient_public_key} {body=}")
        return hash_create(4)

    def publish_stall(self, merchant):
        stall_json = merchant.to_nostr_stall()
        app.logger.info(f"publish_stall id={stall_json['id']} name={stall_json['name']}")
        return hash_create(4)

    def delete_stall(self, merchant):
        app.logger.info(f"delete_stall {merchant.stall_nostr_event_id}")
        return hash_create(4)

    def publish_product(self, entity, extra_media=None):
        product_json = entity.to_nostr(extra_media)
        app.logger.info(f"publish_product name={product_json['name']}")
        return hash_create(4)

    def delete_product(self, entity):
        app.logger.info(f"delete_product {entity.nostr_event_id}")
        return hash_create(4)

    def publish_bid_status(self, _auction, bid_event_id, status, *_, **__):
        app.logger.info(f"publish_bid_status {bid_event_id=} {status=}")
        return hash_create(4)

    def publish_badge_definition(self, badge_id, *_, **__):
        app.logger.info(f"publish_badge_definition {badge_id=}")
        return hash_create(4)

    def publish_badge_award(self, badge_id, pubkey):
        app.logger.info(f"publish_badge_award {badge_id=} {pubkey=}")
        return hash_create(4)

def get_birdwatcher():
    if app.config['ENV'] in ('staging', 'prod'):
        return Birdwatcher(app.config['BIRDWATCHER_BASE_URL'])
    else:
        return MockingBirdwatcher()

def get_site_admin_config():
    if app.config['ENV'] in ('staging', 'prod'):
        with open(app.config['SITE_ADMIN_SECRETS']) as f:
            site_admin = json.load(f)
            return {
                'nostr_private_key': PrivateKey.from_nsec(site_admin['NSEC']),
                'wallet_xpub': site_admin['XPUB'],
                'lightning_address': site_admin['LIGHTNING_ADDRESS'],
            }
    else:
        return {
            'nostr_private_key': PrivateKey(bytes.fromhex("6441b05cc2b810d9d974d9c1308caa555d2beab7994ed10d9e37e945e6477714")),
            'wallet_xpub': "xpub6CUGRUonZSQ4TWtTMmzXdrXDtypWKiKrhko4egpiMZbpiaQL2jkwSB1icqYh2cfDfVxdx4df189oLKnC5fSwqPfgyP3hooxujYzAu3fDVmz",
            'lightning_address': "ibz@stacker.news",
        }

class MockS3:
    def get_url_prefix(self):
        return app.config['API_BASE_URL_EXTERNAL'] + "/mock-s3-files/"

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

class Mail:
    def send(self, to, subject, body, html):
        msg = Message(subject, recipients=[to])
        msg.body = body
        msg.html = html
        mail.send(msg)

class MockMail:
    def send(self, to, subject, body, html):
        app.logger.info(f"Mail: {to=} {subject=} {body=} {html=}")

def get_mail():
    if app.config['MOCK_MAIL']:
        return MockMail()
    else:
        return Mail()

@app.cli.command("lnauth")
@click.argument("lnkey", type=click.STRING)
@with_appcontext
def store_lnauth_key(lnkey):
    """
    For dev env - simplifies passing by the ln-auth system
    Creates a ln auth entry with api key
    :param lnkey: str
    """
    click.echo(f"Setting latest LnAuth key: {lnkey}")
    ln = m.LnAuth.query.order_by(desc(m.LnAuth.created_at)).first()
    ln.key = lnkey
    db.session.commit()

@app.cli.command("lnverify")
@click.argument("lnkey", type=click.STRING)
@with_appcontext
def verify_lnauth_key(lnkey):
    """
    For dev env - simplifies verifying a "fake" lightning wallet.
    """
    click.echo(f"Setting latest key: {lnkey}")
    u = m.User.query.filter(m.User.new_lnauth_key_k1_generated_at != None).order_by(desc(m.User.new_lnauth_key_k1_generated_at)).first()
    u.lnauth_key = u.new_lnauth_key = lnkey
    db.session.commit()

@app.cli.command("award-badge-tester")
@click.argument("pubkey", type=click.STRING)
@with_appcontext
def award_badge_tester(pubkey):
    badge_def = app.config['BADGE_DEFINITION_TESTER']

    badge = m.Badge.query.filter_by(badge_id=badge_def['badge_id']).first()
    if badge is None:
        badge = m.Badge(badge_id=badge_def['badge_id'])
        db.session.add(badge)

    image_response = requests.get(badge_def['image_url'])
    if image_response.status_code != 200:
        click.echo(f"Cannot fetch image at {badge_def['image_url']}!")
        return
    image_data = image_response.content
    sha = hashlib.sha256()
    sha.update(image_data)
    image_hash = sha.hexdigest()

    birdwatcher = get_birdwatcher()
    if badge.name != badge_def['name'] or badge.description != badge_def['description'] or badge.image_hash != image_hash:
        nostr_event_id = birdwatcher.publish_badge_definition(badge_def['badge_id'], badge_def['name'], badge_def['description'], badge_def['image_url'])
        if nostr_event_id is not None:
            badge.name = badge_def['name']
            badge.description = badge_def['description']
            badge.image_hash = image_hash
            badge.nostr_event_id = nostr_event_id
            db.session.commit()
            click.echo("Published badge definition!")
        else:
            click.echo("Failed to publish badge definition!")
            return

    if not birdwatcher.publish_badge_award(badge_def['badge_id'], pubkey):
        click.echo("Failed to publish badge award!")

@app.cli.command("configure-site")
@with_appcontext
def configure_site_cmd():
    configure_site()

def configure_site():
    badge_def = app.config['BADGE_DEFINITION_SKIN_IN_THE_GAME']
    site_admin_config = get_site_admin_config()
    birdwatcher = get_birdwatcher()
    site_admin = m.User.query.filter_by(nostr_public_key=site_admin_config['nostr_private_key'].public_key.hex()).first()
    if site_admin is None:
        site_admin = m.User(nostr_public_key=site_admin_config['nostr_private_key'].public_key.hex(),
                            wallet=site_admin_config['wallet_xpub'],
                            lightning_address=site_admin_config['lightning_address'],
                            stall_name=app.config['SITE_NAME'])
        site_admin.ensure_merchant_key()
        db.session.add(site_admin)
        db.session.commit() # this generates the stall ID
    else:
        app.logger.info("Found site admin user!")

    if site_admin.stall_nostr_event_id is None:
        app.logger.info("Publishing site admin stall...")
        site_admin.stall_nostr_event_id = birdwatcher.publish_stall(site_admin)
        if site_admin.stall_nostr_event_id is None:
            app.logger.error("Error publishing stall to Nostr!")
            return
        app.logger.info(f"Published stall to Nostr! event_id={site_admin.stall_nostr_event_id}")
    else:
        app.logger.info("Found Nostr stall!")

    db.session.commit()

    if app.config['ENV'] == 'test':
        image_hash = hash_create(4)
    else:
        image_response = requests.get(badge_def['image_url'])
        if image_response.status_code != 200:
            app.logger.error(f"Cannot fetch image at {badge_def['image_url']}!")
            return
        image_data = image_response.content
        sha = hashlib.sha256()
        sha.update(image_data)
        image_hash = sha.hexdigest()

    badge_listing = m.Listing.query.join(m.Item).filter((m.Listing.key == badge_def['badge_id']) & (m.Item.seller_id == site_admin.id)).first()
    if badge_listing is None:
        badge_item = m.Item(seller=site_admin, title=badge_def['name'], description=badge_def['description'])
        db.session.add(badge_item)
        db.session.commit()

        badge_media = m.Media(item_id=badge_item.id, index=0, url=badge_def['image_url'], content_hash=image_hash)
        db.session.add(badge_media)
        db.session.commit()

        badge_listing = m.Listing(item=badge_item, key=badge_def['badge_id'], available_quantity=21000000, price_usd=badge_def['price_usd'], start_date=datetime.utcnow())
        db.session.add(badge_listing)
        db.session.commit() # this generates the UUID!
    else:
        app.logger.info("Found badge listing!")

    if badge_listing.nostr_event_id is None:
        badge_listing.nostr_event_id = birdwatcher.publish_product(badge_listing)
        if badge_listing.nostr_event_id is None:
            app.logger.error("Error publishing badge listing to Nostr!")
            return
        app.logger.info(f"Published badge listing to Nostr! event_id={badge_listing.nostr_event_id}")
    else:
        app.logger.info("Found Nostr badge listing!")

    db.session.commit()

    badge = m.Badge.query.filter_by(badge_id=badge_def['badge_id']).first()
    if badge is None:
        badge = m.Badge(badge_id=badge_def['badge_id'], name=badge_def['name'], description=badge_def['description'], image_hash=image_hash)
        badge.nostr_event_id = birdwatcher.publish_badge_definition(badge.badge_id, badge.name, badge.description, badge_def['image_url'])
        if badge.nostr_event_id is None:
            app.logger.error("Failed to publish badge definition!")
            return
        db.session.add(badge)
        db.session.commit()
        app.logger.info(f"Published badge definition to Nostr! event_id={badge.nostr_event_id}")
    else:
        app.logger.info("Found badge!")

if __name__ == '__main__': # dev / test
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

    if app.config['APP'] == 'api' and app.config['ENV'] == 'test':
        with app.app_context():
            app.logger.info("Configuring the site!")
            configure_site()

    app.run(host='0.0.0.0', port=5000, debug=True)
else: # staging / prod
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
