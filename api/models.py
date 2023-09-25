import abc
import bip39gen
import bleach
from collections import OrderedDict
from datetime import datetime, timedelta
import dateutil.parser
from enum import Enum
import hashlib
from io import BytesIO
from itertools import chain
import math
from nostr.key import PrivateKey
import pyqrcode
from slugify import slugify
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import func
import uuid

from extensions import db
from main import app
from utils import hash_create, store_image, parse_xpub, UnknownKeyTypeError

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class AddressGenerationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return f"Error generating address: {self.message}"

class GeneratedKeyMixin:
    def generate_key(self):
        count = db.session.query(func.count(self.__class__.id).label('count')).first().count

        # code taken from https://github.com/supakeen/pinnwand and adapted

        # The amount of bits necessary to store that count times two, then
        # converted to bytes with a minimum of 1.

        # We double the count so that we always keep half of the space
        # available (e.g we increase the number of bytes at 127 instead of
        # 255). This ensures that the probing below can find an empty space
        # fast in case of collision.
        necessary = math.ceil(math.log2((count + 1) * 2)) // 8 + 1

        # Now generate random ids in the range with a maximum amount of
        # retries, continuing until an empty slot is found
        tries = 0

        get_new_key = getattr(self, 'get_new_key', lambda n, _: hash_create(n))

        key = get_new_key(necessary, tries)
        while self.__class__.query.filter_by(key=key).one_or_none():
            app.logger.debug("generate_key: triggered a collision")
            if tries > 10:
                raise RuntimeError("We exceeded our retry quota on a collision.")
            tries += 1
            key = get_new_key(necessary, tries)

        self.key = key

class WalletMixin:
    def get_new_address(self):
        from main import get_btc_client
        btc = get_btc_client()

        try:
            k = parse_xpub(self.wallet)
        except UnknownKeyTypeError as e:
            raise AddressGenerationError(str(e))

        address = None
        while True:
            if self.wallet_index is None:
                self.wallet_index = 0

            address = k.subkey(0).subkey(self.wallet_index).address()
            self.wallet_index += 1

            existing_txs = btc.get_funding_txs(address)

            if existing_txs:
                app.logger.warning("Skipping address with existing txs.")
                continue

            if Sale.query.filter_by(address=address).first():
                app.logger.warning("Skipping address with existing sale.")
                continue

            return address

class State(db.Model):
    __tablename__ = 'state'

    LAST_SETTLE_INDEX = 'LAST_SETTLE_INDEX'
    LAST_PROCESSED_NOTIFICATIONS = 'LAST_PROCESSED_NOTIFICATIONS'

    key = db.Column(db.String(32), primary_key=True)
    value = db.Column(db.String(256), nullable=True)

class LnAuth(db.Model):
    __tablename__ = 'lnauth'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    k1 = db.Column(db.String(128), nullable=False, unique=True, index=True)
    key = db.Column(db.String(128))

class User(WalletMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    lnauth_key = db.Column(db.String(128), unique=True, nullable=True, index=True)

    # fields used when changing the lnauth_key of an existing user
    # (once verified, lnauth_key will become new_lnauth_key and it will be usable for logging in)
    new_lnauth_key = db.Column(db.String(128), unique=False, nullable=True, index=True)
    new_lnauth_key_k1 = db.Column(db.String(128), nullable=True, unique=True, index=True)
    new_lnauth_key_k1_generated_at = db.Column(db.DateTime, nullable=True)

    nostr_public_key = db.Column(db.String(64), unique=True, nullable=True, index=True)

    # TODO: move these to a "wallets" table!
    wallet = db.Column(db.String(128), nullable=True)
    wallet_name = db.Column(db.String(128), nullable=True)
    wallet_index = db.Column(db.Integer, nullable=True)

    lightning_address = db.Column(db.String(64), nullable=True)

    merchant_private_key = db.Column(db.String(64), unique=True, nullable=True, index=True)
    merchant_public_key = db.Column(db.String(64), unique=True, nullable=True, index=True)

    def parse_merchant_private_key(self) -> PrivateKey:
        return PrivateKey(bytes.fromhex(self.merchant_private_key))

    nym = db.Column(db.String(32), unique=True, nullable=True, index=True)

    @property
    def identity(self):
        if self.id is None:
            raise ValueError()
        sha = hashlib.sha256()
        sha.update((str(self.id) + app.config['SECRET_KEY']).encode('UTF-8'))
        return sha.hexdigest()

    @property
    def display_name(self):
        return f"{self.nym}@{app.config['DOMAIN_NAME']}" if app.config['DOMAIN_NAME'] else self.nym

    profile_image_url = db.Column(db.String(256), nullable=True)

    # TODO: move these to a "stalls" table when we decide we need multiple stalls per user

    @property
    def stall_id(self):
        return self.identity # good enough for now, but we should maybe generate it when creating a stall

    stall_nostr_event_id = db.Column(db.String(64), unique=True, nullable=True, index=True)
    stall_banner_url = db.Column(db.String(256), nullable=True)
    stall_name = db.Column(db.String(256), nullable=True)
    stall_description = db.Column(db.String(21000), nullable=True)

    @property
    def stall_currency(self):
        # All fixed-price items are denominated in fiat, at least before we reach some quasi-hyperbitcoinization.
        # NIP-15 actually supports any (fiat) currency,
        # but we think that there is only one fiat currency that matters - the mother of them all.
        # The reasoning behind this is that rather than promoting the idea that there are many currencies in this world,
        # a healthier idea to spread is that there are only two currencies: Bitcoin and fiat.
        # And any fiat currency can easily be converted to USD as part of the UI/UX, if needed.
        return 'USD'

    # TODO: extract these into (per stall?) "shipping zones" as defined in NIP-15
    shipping_from = db.Column(db.String(64), nullable=True)
    shipping_domestic_usd = db.Column(db.Float(), nullable=False, default=0)
    shipping_worldwide_usd = db.Column(db.Float(), nullable=False, default=0)

    def ensure_merchant_key(self):
        if self.merchant_private_key is None:
            self.merchant_private_key = PrivateKey().hex()
        if self.merchant_public_key is None:
            self.merchant_public_key = PrivateKey(bytes.fromhex(self.merchant_private_key)).public_key.hex()

    email = db.Column(db.String(64), unique=True, nullable=True, index=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    email_verification_phrase = db.Column(db.String(32), nullable=True)
    email_verification_phrase_sent_at = db.Column(db.DateTime, nullable=True)
    email_verification_phrase_check_counter = db.Column(db.Integer, nullable=False, default=0)

    def send_email_verification(self):
        from main import get_mail
        body = f"Your email verification phrase is: {self.email_verification_phrase}"
        html = f"""
        <p>Your email verification phrase is: <strong>{self.email_verification_phrase}</strong></p>
        <p>Click <a href="{app.config['WWW_BASE_URL']}/admin/account/verify-email#phrase={self.email_verification_phrase.replace(" ", "%20")}">here</a> to verify your email address!</p>
        """
        get_mail().send(self.email, "Verify your email", body, html)
        self.email_verification_phrase_sent_at = datetime.utcnow()

    telegram_username = db.Column(db.String(64), unique=True, nullable=True, index=True)
    telegram_username_verified = db.Column(db.Boolean, nullable=False, default=False)

    twitter_username = db.Column(db.String(32), unique=True, nullable=True, index=True)
    twitter_username_verified = db.Column(db.Boolean, nullable=False, default=False)

    # NB: this is the (OBSOLETE) private key generated by PM to be used in the chat.
    # if you use a browser extension such as Alby, your private key never even makes it to our API!
    # TODO: remove this!
    nostr_private_key = db.Column(db.String(64), nullable=True)

    def generate_verification_phrase(self, account):
        if account not in ['email']:
            raise ValueError()
        setattr(self, f'{account}_verification_phrase', bip39gen.random_as_string(3))
        setattr(self, f'{account}_verification_phrase_check_counter', 0)
        setattr(self, f'{account}_verification_phrase_sent_at', None)

    contribution_percent = db.Column(db.Float, nullable=True)

    campaigns = db.relationship('Campaign', backref='owner', order_by="desc(Campaign.created_at)")
    items = db.relationship('Item', backref='seller', order_by="desc(Item.created_at)", lazy='dynamic')
    bids = db.relationship('Bid', backref='buyer')
    messages = db.relationship('Message', backref='user')

    def get_contribution_amount(self, for_amount):
        contribution_percent = self.contribution_percent if self.contribution_percent is not None else app.config['CONTRIBUTION_PERCENT_DEFAULT']
        contribution_amount = int(contribution_percent / 100 * for_amount)
        if contribution_amount < app.config['MINIMUM_CONTRIBUTION_AMOUNT']:
            contribution_amount = 0 # probably not worth the fees, at least in the next few years
        return contribution_amount

    def get_relays(self):
        return [{'url': ur.relay.url} for ur in UserRelay.query.filter_by(user_id=self.id).all()]

    def to_nostr_stall(self):
        shipping = [{'id': 'WORLD', 'cost': self.shipping_worldwide_usd, 'regions': ["Worldwide"]}]
        if self.shipping_from and self.shipping_domestic_usd != self.shipping_worldwide_usd:
            domestic_shipping_zone_id = hashlib.sha256(self.shipping_from.encode('utf-8')).hexdigest()
            shipping += [{'id': domestic_shipping_zone_id, 'cost': self.shipping_domestic_usd, 'regions': [self.shipping_from]}]
        return {
            'id': self.stall_id,
            'name': self.stall_name,
            'description': self.stall_description,
            'currency': self.stall_currency,
            'shipping': shipping,
        }

    def to_dict(self, for_user=None):
        assert isinstance(for_user, int | None)

        d = {
            'identity': self.identity,
            'has_lnauth_key': self.lnauth_key is not None, # no reason to return the actual key to the client - just whether there is one or not
            'nostr_public_key': self.nostr_public_key,
            'nym': self.nym,
            'display_name': self.display_name,
            'email': self.email,
            'email_verified': self.email_verified,
            'email_verification_phrase_sent_at': self.email_verification_phrase_sent_at.isoformat() + "Z" if self.email_verification_phrase_sent_at else None,
            'telegram_username': self.telegram_username,
            'telegram_username_verified': self.telegram_username_verified,
            'twitter_username': self.twitter_username,
            'twitter_username_verified': self.twitter_username_verified,
            'stall_banner_url': self.stall_banner_url,
            'stall_name': self.stall_name,
            'stall_description': self.stall_description,
            'has_items': False,
            'has_own_items': False,
            'has_active_auctions': False,
            'has_past_auctions': False,
            'has_active_listings': False,
            'has_past_listings': False,
        }

        for item in self.items.all():
            d['has_items'] = True
            for entity in chain(item.auctions, item.listings):
                if not entity.campaign_id:
                    d['has_own_items'] = True
                if entity.state in ('active', 'past'):
                    d[f'has_{entity.state}_{entity.__tablename__}'] = True
            if d['has_own_items'] and d['has_active_auctions'] and d['has_past_auctions'] and d['has_active_listings'] and d['has_past_listings']:
                break # short-circuit

        if for_user == self.id:
            # only ever show these fields to the actual user
            d['contribution_percent'] = self.contribution_percent
            d['wallet'] = self.wallet
            d['wallet_index'] = self.wallet_index
            d['wallet_name'] = self.wallet_name
            d['lightning_address'] = self.lightning_address
            d['shipping_from'] = self.shipping_from
            d['shipping_domestic_usd'] = self.shipping_domestic_usd
            d['shipping_worldwide_usd'] = self.shipping_worldwide_usd

        return d

class Badge(db.Model):
    __tablename__ = 'badges'

    badge_id = db.Column(db.String(32), nullable=False, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    image_hash = db.Column(db.String(64), nullable=False)
    nostr_event_id = db.Column(db.String(64), nullable=False, unique=True, index=True)

class Relay(db.Model):
    __tablename__ = 'relays'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(128), nullable=False, unique=True, index=True)

class UserRelay(db.Model):
    __tablename__ = 'user_relays'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, primary_key=True)
    relay_id = db.Column(db.Integer, db.ForeignKey(Relay.id), nullable=False, primary_key=True)

    relay = db.relationship('Relay')

class Notification(abc.ABC):
    @property
    @abc.abstractmethod
    def notification_type(self):
        pass

    @property
    @abc.abstractmethod
    def description(self):
        pass

    @property
    def default_action(self):
        return 'TWITTER_DM'

    @abc.abstractmethod
    def get_message_args(self, **kwargs):
        pass

class AuctionEndNotification(Notification):
    @property
    def notification_type(self):
        return 'AUCTION_END'

    @property
    def description(self):
        return "Auction ended"

    def get_message_args(self, **kwargs):
        user, auction, bid = kwargs['user'], kwargs['auction'], kwargs['bid']
        # NB: "bid is None" means this notification refers to an auction
        if bid is None and auction.ended:
            return {
                'user_id': user.id,
                'key': f"{self.notification_type}_{auction.id}",
                'body': f"Auction {auction.item.title} ended! {app.config['WWW_BASE_URL']}/auctions/{auction.key}",
            }

class AuctionEnd10MinNotification(Notification):
    @property
    def notification_type(self):
        return 'AUCTION_END_10MIN'

    @property
    def description(self):
        return "Auction ending in 10 minutes"

    def get_message_args(self, **kwargs):
        user, auction, bid = kwargs['user'], kwargs['auction'], kwargs['bid']
        # NB: "bid is None" means this notification refers to an auction
        if bid is None and auction.end_date <= (datetime.utcnow() + timedelta(minutes=10)):
            return {
                'user_id': user.id,
                'key': f"{self.notification_type}_{auction.id}",
                'body': f"Auction {auction.item.title} ending in less than 10 minutes! {app.config['WWW_BASE_URL']}/auctions/{auction.key}",
            }

class NewBidNotification(Notification):
    @property
    def notification_type(self):
        return 'NEW_BID'

    @property
    def description(self):
        return "New bid"

    def get_message_args(self, **kwargs):
        user, auction, bid = kwargs['user'], kwargs['auction'], kwargs['bid']
        if bid is not None and bid.buyer_id != user.id: # the bidder should not be notified
            return {
                'user_id': user.id,
                'key': f"{self.notification_type}_{auction.id}_{bid.id}",
                'body': f"New bid by {bid.buyer.twitter_username}: {bid.amount} sats! {app.config['WWW_BASE_URL']}/auctions/{auction.key}",
            }

class SaleExpiredNotification(Notification):
    @property
    def notification_type(self):
        return 'SALE_EXPIRED'

    @property
    def description(self):
        return "Sale expired"

    def get_message_args(self, **kwargs):
        user, auction, buyer = kwargs['user'], kwargs['auction'], kwargs['buyer']
        return {
            'user_id': user.id,
            'key': f"{self.notification_type}_{auction.id}_{buyer.id}",
            'body': f"The sale to {buyer.nym} of {auction.item.title} has expired! {app.config['WWW_BASE_URL']}/auctions/{auction.key}",
        }

class PurchaseExpiredNotification(Notification):
    @property
    def notification_type(self):
        return 'PURCHASE_EXPIRED'

    @property
    def description(self):
        return "Purchase expired"

    def get_message_args(self, **kwargs):
        user, auction = kwargs['user'], kwargs['auction']
        return {
            'user_id': user.id,
            'key': f"{self.notification_type}_{auction.id}",
            'body': f"Your purchase of {auction.item.title} has expired!",
        }

class AuctionHasWinnerNotification(Notification):
    @property
    def notification_type(self):
        return 'AUCTION_HAS_WINNER'

    @property
    def description(self):
        return "Auction has winner"

    def get_message_args(self, **kwargs):
        user, auction, buyer = kwargs['user'], kwargs['auction'], kwargs['buyer']
        return {
            'user_id': user.id,
            'key': f"{self.notification_type}_{auction.id}_{buyer.id}",
            'body': f"{buyer.nym} is the winner for {auction.item.title}! Contact him! {app.config['WWW_BASE_URL']}/auctions/{auction.key}",
        }

class AuctionWonNotification(Notification):
    @property
    def notification_type(self):
        return 'AUCTION_WON'

    @property
    def description(self):
        return "Auction won"

    def get_message_args(self, **kwargs):
        user, auction = kwargs['user'], kwargs['auction']
        return {
            'user_id': user.id,
            'key': f"{self.notification_type}_{auction.id}",
            'body': f"You are the winner of {auction.item.title}! {app.config['WWW_BASE_URL']}/auctions/{auction.key}",
        }

class TransactionFoundNotification(Notification):
    @property
    def notification_type(self):
        return 'TRANSACTION_FOUND'

    @property
    def description(self):
        return "Transaction found"

    def get_message_args(self, **kwargs):
        user, sale_id, txid, confirmed = kwargs['user'], kwargs['sale_id'], kwargs['txid'], kwargs['confirmed']
        return {
            'user_id': user.id,
            'key': f"{self.notification_type}_{sale_id}",
            'body': f"We have found your{' ' if confirmed else ' unconfirmed '}transaction {txid} in mempool.space. https://mempool.space/tx/{txid}",
        }

class TransactionConfirmedNotification(Notification):
    @property
    def notification_type(self):
        return 'TRANSACTION_CONFIRMED'

    @property
    def description(self):
        return "Transaction confirmed"

    def get_message_args(self, **kwargs):
        user, sale_id, txid = kwargs['user'], kwargs['sale_id'], kwargs['txid']
        return {
            'user_id': user.id,
            'key': f"{self.notification_type}_{sale_id}",
            'body': f"Your transaction has been confirmed by the network. https://mempool.space/tx/{txid}",
        }

NOTIFICATION_TYPES = OrderedDict([
    (nt.notification_type, nt) for nt in [
        NewBidNotification(),
        AuctionEndNotification(),
        AuctionEnd10MinNotification(),
        SaleExpiredNotification(),
        PurchaseExpiredNotification(),
        AuctionHasWinnerNotification(),
        AuctionWonNotification(),
        TransactionFoundNotification(),
        TransactionConfirmedNotification(),
    ]
])

BACKGROUND_PROCESS_NOTIFICATION_TYPES = {'AUCTION_END', 'AUCTION_END_10MIN', 'NEW_BID'}

class NotificationAction(abc.ABC):
    @property
    @abc.abstractmethod
    def action(self):
        pass

    def to_dict(self):
        return {'action': self.action, 'description': self.description}

    @abc.abstractmethod
    def execute(self, user, message):
        pass

class IgnoreNotificationAction(NotificationAction):
    @property
    def action(self):
        return 'NONE'

    @property
    def description(self):
        return "Ignore"

    def execute(self, user, message):
        # essentially do nothing
        # and return False to let the system know that nothing was sent!
        return False

class InternalNotificationAction(NotificationAction):
    @property
    def action(self):
        return 'INTERNAL'

    @property
    def description(self):
        return "Internal (coming soon)"

    def execute(self, user, message):
        # essentially do nothing,
        # but returning True will make the system think that a notification was sent,
        # thus causing it to save the Message
        return True

NOTIFICATION_ACTIONS = OrderedDict([
    (na.action, na) for na in [IgnoreNotificationAction()]
])

class UserNotification(db.Model):
    __tablename__ = 'user_notifications'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, primary_key=True)
    notification_type = db.Column(db.String(32), nullable=False, primary_key=True)

    # If we want to be able to send the same notification using multiple delivery mechanisms (for example Twitter DM + Telegram)
    # we could, for example, combine multiple actions here (TWITTER_DM|TELEGRAM),
    # then we would simply have to split by "|" when executing the actions in process-notifications!
    # TODO: if we choose to do that, better just rename this field to (maybe) "actions" to make it clear that it does not refer to a single action!
    action = db.Column(db.String(32), nullable=False)

    @classmethod
    def get_action(cls, user_id, notification_type):
        un = db.session.query(cls).filter_by(user_id=user_id, notification_type=notification_type).first()
        return un.action if un else NOTIFICATION_TYPES[notification_type].default_action

    def to_dict(self):
        return {
            'notification_type': self.notification_type,
            'notification_type_description': NOTIFICATION_TYPES[self.notification_type].description,
            'action': self.action,
            'available_actions': [na.to_dict() for na in NOTIFICATION_ACTIONS.values()],
        }

class Message(db.Model):
    __tablename__ = 'messages'

    # NB: this makes sure we never ever send the same notification to the same user twice!
    __table_args__ = (db.UniqueConstraint('user_id', 'key'),)

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # The "key" of a message is the notification type combined with auction/bid IDs relevant to that notification
    # for example, for an AUCTION_END notification, we would combine that to the auction ID.
    key = db.Column(db.String(64), nullable=False)

    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    body = db.Column(db.String(512), nullable=True)

    # the action used to send this notification (for example TWITTER_DM)
    # NB: this is NULL if the send failed
    notified_via = db.Column(db.String(32), nullable=True)

    @classmethod
    def create_and_send(cls, notification_type, user, **kwargs):
        notification = NOTIFICATION_TYPES[notification_type]

        message_args = notification.get_message_args(user=user, **kwargs)
        if not message_args:
            return

        message = cls(**message_args)
        db.session.add(message)

        try:
            db.session.commit() # this is done before actually sending the message, to ensure uniqueness

            action = UserNotification.get_action(user.id, notification_type)
            app.logger.info(f"Executing {action=} for {user.id=}!")
            if action in NOTIFICATION_ACTIONS and NOTIFICATION_ACTIONS[action].execute(user, message):
                app.logger.info(f"Notified {user.id=} with {action=}!")
                message.notified_via = action
                db.session.commit()
        except IntegrityError:
            app.logger.warning(f"Duplicate message send attempt: {message_args['key']=} {message_args['user_id']=}!")
            db.session.rollback()

    def to_dict(self):
        return {
            'key': self.key,
            'created_at': self.created_at.isoformat() + "Z",
            'body': self.body,
            'notified_via': self.notified_via,
        }

class StateMixin:
    @property
    def state(self):
        if not self.started and not self.ended:
            return 'new'
        elif self.started and not self.ended:
            return 'active'
        elif self.ended:
            return 'past'

    def filter_state(self, state, for_user_id):
        is_owner = for_user_id == self.owner_id
        if state is None:
            return True if is_owner else self.state != 'new'
        elif state == 'new':
            return self.state == 'new' if is_owner else False
        else:
            return self.state == state

class Campaign(WalletMixin, GeneratedKeyMixin, StateMixin, db.Model):
    __tablename__ = 'campaigns'

    REQUIRED_FIELDS = ['wallet', 'name', 'description']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    @property
    def nostr_event_id(self):
        return None

    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    key = db.Column(db.String(24), unique=True, nullable=False, index=True)

    def get_new_key(self, _, tries):
        match tries:
            case 0:
                return slugify(self.name)
            case tries if tries <= 5:
                return f"{slugify(self.name)}-{tries}"
            case _:
                return f"{slugify(self.name)}-{hash_create(1)}"

    banner_url = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(210), nullable=False)
    description = db.Column(db.String(21000), nullable=False)

    wallet = db.Column(db.String(128), nullable=False)
    wallet_index = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    auctions = db.relationship('Auction', backref='campaign')
    listings = db.relationship('Listing', backref='campaign')

    def sort_key(self):
        return self.created_at

    @classmethod
    def query_all_active(cls):
        return cls.query

    def to_dict(self, for_user=None):
        campaign = {
            'key': self.key,
            'banner_url': self.banner_url,
            'name': self.name,
            'description': self.description,
            'wallet': self.wallet,
            'wallet_index': self.wallet_index,
            'created_at': self.created_at.isoformat() + "Z",
            'is_mine': for_user == self.owner_id,
            'owner_nym': self.owner.nym,
            'owner_display_name': self.owner.display_name,
            'owner_email': self.owner.email,
            'owner_email_verified': self.owner.email_verified,
            'owner_telegram_username': self.owner.telegram_username,
            'owner_telegram_username_verified': self.owner.telegram_username_verified,
            'owner_twitter_username': self.owner.twitter_username,
            'owner_twitter_username_verified': self.owner.twitter_username_verified,
        }

        return campaign

    @classmethod
    def validate_dict(cls, d, for_method=None):
        validated = {}
        for k in ['name', 'description']:
            if k not in d:
                continue
            length = len(d[k])
            max_length = getattr(Campaign, k).property.columns[0].type.length
            if length > max_length:
                raise ValidationError(f"Please keep the {k} below {max_length} characters. You are currently at {length}.")
            validated[k] = d[k]
        if for_method == 'POST' and 'wallet' in d: # xpub can only be set once, on POST
            try:
                k = parse_xpub(d['wallet'])
            except UnknownKeyTypeError as e:
                raise ValidationError("Invalid XPUB.")
            try:
                _ = k.subkey(0).subkey(0).address()
            except AttributeError:
                raise ValidationError("Invalid XPUB.")
            validated['wallet'] = d['wallet']
            validated['wallet_index'] = 0
        return validated

class Category(Enum):
    Time = 'TIME'

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    title = db.Column(db.String(210), nullable=False)
    description = db.Column(db.String(21000), nullable=False)
    category = db.Column(db.String(21), nullable=True)

    extra_shipping_domestic_usd = db.Column(db.Float(), nullable=False, default=0)
    extra_shipping_worldwide_usd = db.Column(db.Float(), nullable=False, default=0)

    media = db.relationship('Media', backref='item', foreign_keys='Media.item_id', order_by="Media.index")

    is_hidden = db.Column(db.Boolean, nullable=False, default=False)

    auctions = db.relationship('Auction', backref='item')
    listings = db.relationship('Listing', backref='item')

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        for k in ['title', 'description', 'category']:
            if k not in d:
                continue
            length = len(d[k])
            max_length = getattr(Item, k).property.columns[0].type.length
            if length > max_length:
                raise ValidationError(f"Please keep the {k} below {max_length} characters. You are currently at {length}.")
            validated[k] = bleach.clean(d[k])
        for k in ['extra_shipping_domestic_usd', 'extra_shipping_worldwide_usd']:
            if k not in d:
                continue
            try:
                validated[k] = float(d[k])
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        for k in ['is_hidden']:
            if k not in d:
                continue
            try:
                validated[k] = bool(int(d[k]))
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        return validated

class Auction(GeneratedKeyMixin, StateMixin, db.Model):
    __tablename__ = 'auctions'

    REQUIRED_FIELDS = ['title', 'description', 'duration_hours', 'starting_bid', 'reserve_bid', 'extra_shipping_domestic_usd', 'extra_shipping_worldwide_usd']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    uuid = db.Column(UUID(as_uuid=True), nullable=False, unique=True, index=True, default=uuid.uuid4)
    nostr_event_id = db.Column(db.String(64), unique=True, nullable=True, index=True)

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=False)

    @property
    def owner_id(self):
        return self.item.seller_id

    # this key uniquely identifies the auction. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=True)

    # this is set on "publish"
    start_date = db.Column(db.DateTime, nullable=True)

    @property
    def started(self):
        return self.start_date <= datetime.utcnow() if self.start_date else False

    # duration_hours reflects the initial duration,
    # but the auction can be extended when bids come in close to the end - hence the end_date
    duration_hours = db.Column(db.Float, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)

    def extend(self):
        if self.end_date:
            if self.end_date < datetime.utcnow() + timedelta(minutes=app.config['BID_LAST_MINUTE_EXTEND']):
                old_end_date = self.end_date
                self.end_date = datetime.utcnow() + timedelta(minutes=app.config['BID_LAST_MINUTE_EXTEND'])
                return (self.end_date - old_end_date).total_seconds()
        return 0

    @property
    def ended(self):
        return self.end_date < datetime.utcnow() if self.end_date else False

    starting_bid = db.Column(db.Integer, nullable=False)
    reserve_bid = db.Column(db.Integer, nullable=False)

    skin_in_the_game_required = db.Column(db.Boolean, nullable=False, default=False)

    twitter_id = db.Column(db.String(32), nullable=True)

    # None: winner not decided yet; True: winner was decided; False: nobody won
    has_winner = db.Column(db.Boolean, nullable=True, default=None)

    winning_bid_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    bids = db.relationship('Bid', backref='auction', foreign_keys='Bid.auction_id', order_by='desc(Bid.amount)')

    user_auctions = db.relationship('UserAuction', cascade="all,delete", backref='auction')

    sales = db.relationship('Sale', backref='auction', order_by="Sale.requested_at")

    def get_top_bid(self, below=None):
        return max((bid for bid in self.bids if bid.settled_at and (below is None or bid.amount < below)), default=None, key=lambda bid: bid.amount)

    def get_winning_bid(self):
        return [b for b in self.bids if b.id == self.winning_bid_id][0] if self.winning_bid_id else None

    def sort_key(self):
        return self.start_date

    def featured_sort_key(self):
        # show new auctions at the top
        return -self.start_date.timestamp()

    def get_not_editable_reason(self):
        if len(self.bids) > 0:
            return "Cannot edit auctions that already have bids."

    @property
    def reserve_bid_reached(self):
        if self.reserve_bid == 0:
            return True
        top_bid = self.get_top_bid()
        return top_bid.amount >= self.reserve_bid if top_bid else False

    @property
    def nostr_event_kind(self):
        return 31020 if app.config['ENV'] == 'staging' else 30020

    def to_nostr(self, extra_media=None):
        if extra_media is None:
            extra_media = []
        return {
            'id': str(self.uuid),
            'stall_id': self.item.seller.stall_id,
            'name': self.item.title,
            'description': self.item.description,
            'images': [media.url for media in self.item.media] + [media.url for media in extra_media],
            'starting_bid': self.starting_bid,
            'start_date': int(self.start_date.timestamp()) if self.start_date else None,
            'duration': self.duration_hours * 60 * 60,
            'shipping': [
                {
                    'id': hashlib.sha256(self.item.seller.shipping_from.encode('utf-8')).hexdigest() if self.item.seller.shipping_from else "",
                    'cost': self.item.extra_shipping_domestic_usd,
                },
                {
                    'id': 'WORLD',
                    'cost': self.item.extra_shipping_worldwide_usd,
                },
            ]
        }

    def to_dict(self, for_user=None):
        if not self.started:
            ends_in_seconds = None
        elif self.ended:
            ends_in_seconds = 0
        else:
            ends_in_seconds = (self.end_date - datetime.utcnow()).total_seconds()
        auction = {
            'merchant_public_key': self.item.seller.merchant_public_key,
            'uuid': str(self.uuid),
            'nostr_event_id': self.nostr_event_id,
            'key': self.key,
            'title': self.item.title,
            'description': self.item.description,
            'category': self.item.category,
            'duration_hours': self.duration_hours,
            'skin_in_the_game_required': self.skin_in_the_game_required,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'started': self.started,
            'end_date': self.end_date.isoformat() + "Z" if self.end_date else None,
            'end_date_extended': self.end_date > self.start_date + timedelta(hours=self.duration_hours) if self.start_date else False,
            'ended': self.ended,
            'ends_in_seconds': ends_in_seconds,
            'starting_bid': self.starting_bid,
            'reserve_bid_reached': self.reserve_bid_reached,
            'extra_shipping_domestic_usd': self.item.extra_shipping_domestic_usd,
            'extra_shipping_worldwide_usd': self.item.extra_shipping_worldwide_usd,
            'has_winner': self.has_winner,
            'bids': [bid.to_dict() for bid in self.bids if bid.settled_at],
            'created_at': self.created_at.isoformat() + "Z",
            'campaign_key': self.campaign.key if self.campaign else None,
            'campaign_name': self.campaign.name if self.campaign else None,
            'is_mine': for_user == self.item.seller_id if for_user else False,
        }

        if self.item.category == Category.Time.value:
            auction['media'] = [{'index': 0, 'hash': 'TODO', 'url': self.item.seller.profile_image_url}]
        else:
            auction['media'] = [media.to_dict() for media in self.item.media]

        if for_user == self.owner_id:
            auction['reserve_bid'] = self.reserve_bid

        if auction['has_winner']:
            winning_bid = [b for b in self.bids if b.id == self.winning_bid_id][0]
            if winning_bid.buyer_id: # old style
                auction['winner_nym'] = winning_bid.buyer.nym
                auction['winner_display_name'] = winning_bid.buyer.display_name
                auction['winner_email'] = winning_bid.buyer.email
                auction['winner_email_verified'] = winning_bid.buyer.email_verified
                auction['winner_telegram_username'] = winning_bid.buyer.telegram_username
                auction['winner_telegram_username_verified'] = winning_bid.buyer.telegram_username_verified
                auction['winner_twitter_username'] = winning_bid.buyer.twitter_username
                auction['winner_twitter_username_verified'] = winning_bid.buyer.twitter_username_verified
                auction['winner_nostr_public_key'] = winning_bid.buyer.nostr_public_key
            else:
                auction['winner_nym'] = winning_bid.buyer_nostr_public_key

        return auction

    @classmethod
    def query_all_active(cls):
        q = (cls.start_date != None) & (cls.start_date <= datetime.utcnow()) & (cls.end_date > datetime.utcnow())
        return cls.query.filter(q)

    @classmethod
    def query_all_inactive(cls):
        q = (cls.start_date != None) & (cls.start_date <= datetime.utcnow()) & (cls.end_date <= datetime.utcnow())
        return cls.query.filter(q)

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        for k in ['start_date']:
            # for now, only start_date can be edited
            # the end_date is computed on auction start using duration_hours
            if k not in d:
                continue
            try:
                date = dateutil.parser.isoparse(d[k])
                if date.tzinfo != dateutil.tz.tzutc():
                    raise ValidationError(f"Date must be in UTC: {k.replace('_', ' ')}.")
                date = date.replace(tzinfo=None)
            except ValueError:
                raise ValidationError(f"Invalid {k.replace('_', ' ')}.")
            validated[k] = date
        for k in ['starting_bid', 'reserve_bid']:
            if k not in d:
                continue
            try:
                validated[k] = int(d[k])
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        for k in ['duration_hours']:
            if k not in d:
                continue
            try:
                validated[k] = float(d[k])
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        if 'start_date' in validated and 'duration_hours' in validated:
            validated['end_date'] = validated['start_date'] + timedelta(hours=validated['duration_hours'])
        for k in ['skin_in_the_game_required']:
            if k not in d:
                continue
            try:
                validated[k] = bool(int(d[k]))
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        return validated

class Listing(GeneratedKeyMixin, StateMixin, db.Model):
    __tablename__ = 'listings'

    REQUIRED_FIELDS = ['title', 'description', 'price_usd', 'available_quantity', 'extra_shipping_domestic_usd', 'extra_shipping_worldwide_usd']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    uuid = db.Column(UUID(as_uuid=True), nullable=False, unique=True, index=True, default=uuid.uuid4)
    nostr_event_id = db.Column(db.String(64), unique=True, nullable=True, index=True)

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=False)

    @property
    def owner_id(self):
        return self.item.seller_id

    # this key uniquely identifies the listing. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=True)

    start_date = db.Column(db.DateTime, nullable=True)

    @property
    def started(self):
        return self.start_date <= datetime.utcnow() if self.start_date else False

    @property
    def ended(self):
        return self.available_quantity == 0

    price_usd = db.Column(db.Float, nullable=False)
    available_quantity = db.Column(db.Integer, nullable=False)

    twitter_id = db.Column(db.String(32), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sales = db.relationship('Sale', backref='listing', order_by="Sale.requested_at")

    def sort_key(self):
        return self.start_date

    def featured_sort_key(self):
        # reverse sort - newer listings show at the top
        return -self.start_date.timestamp()

    @property
    def nostr_event_kind(self):
        return 31018 if app.config['ENV'] == 'staging' else 30018

    def to_nostr(self, extra_media=None):
        if extra_media is None:
            extra_media = []
        return {
            'id': str(self.uuid),
            'stall_id': self.item.seller.stall_id,
            'name': self.item.title,
            'description': self.item.description,
            'images': [media.url for media in self.item.media] + [media.url for media in extra_media],
            'currency': 'USD',
            'price': self.price_usd,
            'quantity': self.available_quantity,
            'shipping': [
                {
                    'id': hashlib.sha256(self.item.seller.shipping_from.encode('utf-8')).hexdigest() if self.item.seller.shipping_from else "",
                    'cost': self.item.extra_shipping_domestic_usd,
                },
                {
                    'id': 'WORLD',
                    'cost': self.item.extra_shipping_worldwide_usd,
                },
            ]
        }

    def to_dict(self, for_user=None):
        assert isinstance(for_user, int | None)

        listing = {
            'merchant_public_key': self.item.seller.merchant_public_key,
            'uuid': str(self.uuid),
            'nostr_event_id': self.nostr_event_id,
            'key': self.key,
            'title': self.item.title,
            'description': self.item.description,
            'category': self.item.category,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'started': self.started,
            'ended': self.ended,
            'price_usd': self.price_usd,
            'available_quantity': self.available_quantity,
            'extra_shipping_domestic_usd': self.item.extra_shipping_domestic_usd,
            'extra_shipping_worldwide_usd': self.item.extra_shipping_worldwide_usd,
            'created_at': self.created_at.isoformat() + "Z",
            'campaign_key': self.campaign.key if self.campaign else None,
            'campaign_name': self.campaign.name if self.campaign else None,
            'is_mine': for_user == self.item.seller_id,
        }
        if self.item.category == Category.Time.value:
            listing['media'] = [{'index': 0, 'hash': 'TODO', 'url': self.item.seller.profile_image_url}]
        else:
            listing['media'] = [media.to_dict() for media in self.item.media]

        return listing

    @classmethod
    def query_all_active(cls):
        q = (cls.start_date != None) & (cls.start_date <= datetime.utcnow()) & (cls.available_quantity != 0)
        return cls.query.filter(q)

    @classmethod
    def query_all_inactive(cls):
        q = (cls.start_date != None) & (cls.start_date <= datetime.utcnow()) & (cls.available_quantity == 0)
        return cls.query.filter(q)

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        for k in ['available_quantity']:
            if k not in d:
                continue
            try:
                validated[k] = int(d[k])
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
            if validated[k] < 0:
                raise ValidationError(f"{k.replace('_', ' ')} needs to be greater than zero.".capitalize())
        for k in ['price_usd']:
            if k not in d:
                continue
            try:
                validated[k] = float(d[k])
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        for k in ['active']:
            if k not in d:
                continue
            try:
                validated[k] = bool(int(d[k]))
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        return validated

class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=False)

    index = db.Column(db.Integer, nullable=False)

    # TODO: make non-nullable
    content_hash = db.Column(db.String(256), nullable=True)

    twitter_media_key = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(256), nullable=False)

    def to_dict(self):
        return {
            'hash': self.content_hash,
            'index': self.index,
            'url': self.url,
        }

    def store(self, s3, filename, original_filename, data):
        self.url, self.content_hash = store_image(s3, filename, False, original_filename, data)
        return self.url is not None

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    nostr_event_id = db.Column(db.String(64), unique=True, nullable=True, index=True)

    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=False)

    # NB: this is not used anymore as bids are now placed on Nostr!
    buyer_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)

    buyer_nostr_public_key = db.Column(db.String(64), nullable=True, index=True)

    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime) # a bid is settled instantly unless "skin in the game" is needed

    amount = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'amount': self.amount,
            'buyer_nym': self.buyer.nym if self.buyer else None,
            'buyer_display_name': self.buyer.display_name if self.buyer else None,
            'buyer_email': self.buyer.email if self.buyer else None,
            'buyer_email_verified': self.buyer.email_verified if self.buyer else None,
            'buyer_telegram_username': self.buyer.telegram_username if self.buyer else None,
            'buyer_telegram_username_verified': self.buyer.telegram_username_verified if self.buyer else None,
            'buyer_twitter_username': self.buyer.twitter_username if self.buyer else None,
            'buyer_twitter_username_verified': self.buyer.twitter_username_verified if self.buyer else None,
            'buyer_nostr_public_key': self.buyer.nostr_public_key if self.buyer else None,
            'settled_at': (self.settled_at.isoformat() + "Z" if self.settled_at else None),
            'is_winning_bid': self.id == self.auction.winning_bid_id,
        }

class Order(db.Model):
    """
        Orders come in via Nostr NIP-15.
        The difference from old-style "Sales" is mostly that the buyer doesn't need to be a user in our backend,
        and an order can have more than one item being sold at the same time.
    """

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # NB: this is string, not UUID, because it is generated by the buyer
    # TODO: should we make it unique=False for this very reason,
    # so there is no chance of clash between orders of different users if they don't use random enough "UUID"s?
    uuid = db.Column(db.String(36), unique=True, nullable=False, index=True)

    # NB: orders contain items which are all from the same seller, so we denormalize seller_id here for simplicity
    seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    event_id = db.Column(db.String(64), nullable=False, index=True)
    buyer_public_key = db.Column(db.String(64), nullable=False, index=True)

    buyer_name = db.Column(db.String(64), nullable=True)
    buyer_address = db.Column(db.String(256), nullable=True)
    buyer_message = db.Column(db.String(512), nullable=True)
    buyer_contact = db.Column(JSON, nullable=True)

    on_chain_address = db.Column(db.String(128), nullable=True, unique=True, index=True)
    lightning_address = db.Column(db.String(128), nullable=True, index=True)

    txid = db.Column(db.String(128), nullable=True)
    tx_value = db.Column(db.Integer, nullable=True)
    tx_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    requested_at = db.Column(db.DateTime, nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)
    shipped_at = db.Column(db.DateTime, nullable=True)
    expired_at = db.Column(db.DateTime, nullable=True)
    canceled_at = db.Column(db.DateTime, nullable=True)

    shipping_usd = db.Column(db.Float, nullable=False, default=0)

    total_usd = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False, default=0)

    order_items = db.relationship('OrderItem', backref='order')

    seller = db.relationship('User')
    invoices = db.relationship('LightningInvoice', back_populates="order",  order_by="desc(LightningInvoice.created_at)")
    payment_logs = db.relationship('LightningPaymentLog', back_populates="order", order_by="desc(LightningPaymentLog.created_at)")

    @property
    def timeout_minutes(self):
        if self.txid:
            # if we already have a TX (without confirmations though),
            # we can give it more time to confirm...

            match app.config['ENV']:
                case 'dev':
                    return 10
                case 'staging':
                    return 60 # need more time to confirm - they are real TXes in staging!
                case _:
                    return 48 * 60

        return 24 * 60

    def has_skin_in_the_game_badge(self):
        for order_item in self.order_items:
            if order_item.listing_id is not None and order_item.listing.key == app.config['BADGE_DEFINITION_SKIN_IN_THE_GAME']['badge_id']:
                return True

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'event_id': self.event_id,
            'buyer': {
                'public_key': self.buyer_public_key,
                'name': self.buyer_name,
                'address': self.buyer_address,
                'message': self.buyer_message,
                'contact': self.buyer_contact,
            },
            'on_chain_address': self.on_chain_address,
            'txid': self.txid,
            'tx_value': self.tx_value,
            'requested_at': (self.requested_at.isoformat() + "Z"),
            'paid_at': (self.paid_at.isoformat() + "Z" if self.paid_at else None),
            'shipped_at': (self.shipped_at.isoformat() + "Z" if self.shipped_at else None),
            'expired_at': (self.expired_at.isoformat() + "Z" if self.expired_at else None),
            'canceled_at': (self.canceled_at.isoformat() + "Z" if self.canceled_at else None),
            'total_usd': self.total_usd,
            'total': self.total,
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    order_id = db.Column(db.Integer, db.ForeignKey(Order.id), nullable=False)

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=False)
    item = db.relationship('Item')

    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=True)
    auction = db.relationship('Auction')

    listing_id = db.Column(db.Integer, db.ForeignKey(Listing.id), nullable=True)
    listing = db.relationship('Listing')

    quantity = db.Column(db.Integer, nullable=False)

class SaleState(Enum):
    OLD = -1 # old sales, from before we used to settle on-chain
    REQUESTED = 0
    CONTRIBUTION_SETTLED = 1
    TX_DETECTED = 2
    TX_CONFIRMED = 3
    EXPIRED = 4

class Sale(db.Model):
    """
        Sales are old-style (pre-NIP-15) orders, used to purchase items directly from our API.
    """

    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=True)
    listing_id = db.Column(db.Integer, db.ForeignKey(Listing.id), nullable=True)

    desired_badge = db.Column(db.Integer, nullable=True)

    @property
    def is_auction_sale(self):
        return self.auction_id is not None

    @property
    def is_listing_sale(self):
        return self.listing_id is not None

    @property
    def is_badge_sale(self):
        return self.desired_badge is not None

    # this is used when donating money to a campaign without buying anything (for the purpose of getting a campaign badge)
    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=True)

    buyer_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    state = db.Column(db.Integer, nullable=False, default=SaleState.REQUESTED.value)

    txid = db.Column(db.String(128), nullable=True)
    tx_value = db.Column(db.Integer, nullable=True)

    settled_at = db.Column(db.DateTime, nullable=True) # a sale is settled after the transaction has been confirmed
    expired_at = db.Column(db.DateTime, nullable=True)

    address = db.Column(db.String(128), nullable=False, unique=True, index=True)

    price_usd = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    amount = db.Column(db.Integer, nullable=False) # amount to be paid (total amount minus contribution) *not* including shipping
    shipping_domestic = db.Column(db.Integer, nullable=False)
    shipping_worldwide = db.Column(db.Integer, nullable=False)

    # the Lightning invoice for the contribution
    contribution_amount = db.Column(db.Integer, nullable=False)
    contribution_payment_request = db.Column(db.String(512), nullable=True, unique=True, index=True)
    contribution_settled_at = db.Column(db.DateTime, nullable=True) # this is NULL initially, and gets set after the contribution has been received

    @property
    def timeout_minutes(self):
        if self.txid:
            # if we already have a TX (without confirmations though),
            # we can give it more time to confirm...

            match app.config['ENV']:
                case 'dev':
                    return 10
                case 'staging':
                    return 60 # need more time to confirm - they are real TXes in staging!
                case _:
                    return 48 * 60

        if app.config['ENV'] in ['dev', 'staging']:
            return 10 # 10 mins should be enough to send a 0-conf
        else: # prod
            if self.is_listing_sale or self.is_badge_sale:
                return 30
            else: # auction - you might not be around when you win it!
                return 24 * 60 # one day for a 0-conf to appear in the mempool

    def to_dict(self):
        sale = {
            'item_title': self.item.title if self.item else None,
            'desired_badge': self.desired_badge,
            'campaign_key': self.campaign.key if self.campaign else None,
            'campaign_name': self.campaign.name if self.campaign else None,
            'state': SaleState(self.state).name,
            'price_usd': self.price_usd,
            'price': self.price,
            'quantity': self.quantity,
            'amount': self.amount,
            'shipping_domestic': self.shipping_domestic,
            'shipping_worldwide': self.shipping_worldwide,
            'seller_nym': self.item.seller.nym if self.item else None,
            'seller_display_name': self.item.seller.display_name if self.item else None,
            'seller_email': self.item.seller.email if self.item else None,
            'seller_email_verified': self.item.seller.email_verified if self.item else False,
            'seller_telegram_username': self.item.seller.telegram_username if self.item else None,
            'seller_telegram_username_verified': self.item.seller.telegram_username_verified if self.item else False,
            'seller_twitter_username': self.item.seller.twitter_username if self.item else None,
            'seller_twitter_username_verified': self.item.seller.twitter_username_verified if self.item else False,
            'seller_nostr_public_key': self.item.seller.nostr_public_key if self.item else None,
            'buyer_nym': self.buyer.nym,
            'buyer_display_name': self.buyer.display_name,
            'buyer_email': self.buyer.email,
            'buyer_email_verified': self.buyer.email_verified,
            'buyer_telegram_username': self.buyer.telegram_username,
            'buyer_telegram_username_verified': self.buyer.telegram_username_verified,
            'buyer_twitter_username': self.buyer.twitter_username,
            'buyer_twitter_username_verified': self.buyer.twitter_username_verified,
            'buyer_nostr_public_key': self.buyer.nostr_public_key,
            'contribution_amount': self.contribution_amount,
            'contribution_payment_request': self.contribution_payment_request,
            'contribution_settled_at': (self.contribution_settled_at.isoformat() + "Z" if self.contribution_settled_at else None),
            'address': self.address,
            'requested_at': (self.requested_at.isoformat() + "Z"),
            'settled_at': (self.settled_at.isoformat() + "Z" if self.settled_at else None),
            'txid': self.txid,
            'tx_value': self.tx_value,
            'expired_at': (self.expired_at.isoformat() + "Z" if self.expired_at else None),
        }

        if self.auction:
            sale['item_url'] = f"/auctions/{self.auction.key}"
        elif self.listing:
            sale['item_url'] = f"/listings/{self.listing.key}"
        else:
            # probably a badge sale
            sale['item_url'] = None

        if self.state == SaleState.REQUESTED.value:
            contribution_payment_qr = BytesIO()
            pyqrcode.create(self.contribution_payment_request).svg(contribution_payment_qr, omithw=True, scale=4)
            sale['contribution_payment_qr'] = contribution_payment_qr.getvalue().decode('utf-8')
        elif self.state == SaleState.CONTRIBUTION_SETTLED.value:
            for which, shipping in [("", 0), ("_domestic", 1 / app.config['SATS_IN_BTC'] * self.shipping_domestic), ("_worldwide", 1 / app.config['SATS_IN_BTC'] * self.shipping_worldwide)]:
                qr = BytesIO()
                pyqrcode.create(f"bitcoin:{self.address}?amount={1 / app.config['SATS_IN_BTC'] * self.amount + shipping :.9f}").svg(qr, omithw=True, scale=4)
                sale[f'qr{which}'] = qr.getvalue().decode('utf-8')

        return sale

class UserAuction(db.Model):
    __tablename__ = 'user_auctions'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=False, primary_key=True)

    following = db.Column(db.Boolean, nullable=False)

class LightningInvoice(db.Model):
    __tablename__ = 'lightning_invoices'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    order_id = db.Column(db.Integer, db.ForeignKey(Order.id), nullable=False, primary_key=True)

    invoice = db.Column(db.String, nullable=False)
    payment_hash = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # TODO is this needed?
    paid = db.Column(db.Boolean, nullable=False, default=False)

    order = db.relationship('Order', back_populates="invoices")

class LightningPaymentLogState(Enum):
    RECEIVED = 0
    SELLER_PAID = 1
    OTHER_PAID = 2

class LightningPaymentLog(db.Model):
    __tablename__ = 'lightning_payment_logs'

    # id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    order_id = db.Column(db.Integer, db.ForeignKey(Order.id), nullable=False, primary_key=True)
    lightning_invoice_id = db.Column(db.Integer, db.ForeignKey(LightningInvoice.id), nullable=False, primary_key=True)
    state = db.Column(db.Integer, nullable=False)
    paid_to = db.Column(db.String(200), nullable=False, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order = db.relationship('Order', back_populates="payment_logs")
