import abc
import bip39gen
import bleach
from collections import OrderedDict
from datetime import datetime, timedelta
import dateutil.parser
from enum import Enum
from io import BytesIO
from itertools import chain
import math
from pycoin.symbols.btc import network as BTC
import pyqrcode
import random
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import func
import string

from extensions import db
from main import app
from utils import hash_create, store_image

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class XpubMixin:
    def get_new_address(self):
        from main import get_btc_client
        btc = get_btc_client()
        k = BTC.parse(self.xpub)
        address = None
        while True:
            if self.xpub_index is None:
                self.xpub_index = 0

            address = k.subkey(0).subkey(self.xpub_index).address()
            self.xpub_index += 1

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

    EXPIRE_MINUTES = 10

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    k1 = db.Column(db.String(128), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    key = db.Column(db.String(128))

class User(XpubMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Lightning log in key
    key = db.Column(db.String(128), unique=True, nullable=False, index=True)

    # ask Pedro about this
    xpub = db.Column(db.String(128), nullable=True)
    xpub_index = db.Column(db.Integer, nullable=True)

    nym = db.Column(db.String(32), unique=True, nullable=True, index=True)

    @property
    def display_name(self):
        return f"{self.nym}@{app.config['DOMAIN_NAME']}" if app.config['DOMAIN_NAME'] else self.nym

    # TODO: rename to profile_image_url
    twitter_profile_image_url = db.Column(db.String(256), nullable=True)

    stall_banner_url = db.Column(db.String(256), nullable=True)
    stall_name = db.Column(db.String(256), nullable=True)
    stall_description = db.Column(db.String(21000), nullable=True)

    email = db.Column(db.String(64), unique=True, nullable=True, index=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)

    telegram_username = db.Column(db.String(64), unique=True, nullable=True, index=True)
    telegram_username_verified = db.Column(db.Boolean, nullable=False, default=False)

    twitter_username = db.Column(db.String(32), unique=True, nullable=True, index=True)
    twitter_username_verified = db.Column(db.Boolean, nullable=False, default=False)
    twitter_verification_phrase = db.Column(db.String(32), nullable=True)
    twitter_verification_phrase_sent_at = db.Column(db.DateTime, nullable=True)
    twitter_verification_phrase_check_counter = db.Column(db.Integer, nullable=False, default=0)

    def generate_twitter_verification_phrase(self):
        self.twitter_verification_phrase = bip39gen.random_as_string(3)
        self.twitter_verification_phrase_check_counter = 0
        self.twitter_verification_phrase_sent_at = None

    @property
    def is_moderator(self):
        return (self.id in app.config['MODERATOR_USER_IDS']) or ('ALL' in app.config['MODERATOR_USER_IDS'])

    contribution_percent = db.Column(db.Float, nullable=True)

    campaigns = db.relationship('Campaign', backref='owner', order_by="desc(Campaign.created_at)")
    items = db.relationship('Item', backref='seller', order_by="desc(Item.created_at)", lazy='dynamic')
    auctions = db.relationship('Auction', backref='seller', order_by="desc(Auction.created_at)", lazy='dynamic')
    bids = db.relationship('Bid', backref='buyer')
    messages = db.relationship('Message', backref='user')

    sales = db.relationship('Sale', backref='buyer', order_by="Sale.requested_at")

    def fetch_twitter_profile_image(self, profile_image_url, s3):
        url, _ = store_image(s3, f"user_{self.id}_twitter_profile_image", True, profile_image_url, None)
        if not url:
            return False
        self.twitter_profile_image_url = url
        return True

    def fetch_twitter_profile_banner(self, profile_banner_url, s3):
        if profile_banner_url:
            url, _ = store_image(s3, f"user_{self.id}_stall_banner", True, profile_banner_url, None)
            if not url:
                return False
        else:
            url = None
        self.stall_banner_url = url
        return True

    def get_contribution_amount(self, for_amount):
        contribution_percent = self.contribution_percent if self.contribution_percent is not None else app.config['CONTRIBUTION_PERCENT_DEFAULT']
        contribution_amount = int(contribution_percent / 100 * for_amount)
        if contribution_amount < app.config['MINIMUM_CONTRIBUTION_AMOUNT']:
            contribution_amount = 0 # probably not worth the fees, at least in the next few years
        return contribution_amount

    def get_badges(self):
        return [{'badge': b.badge, 'icon': b.icon, 'awarded_at': b.awarded_at}
            for b in UserBadge.query.filter_by(user_id=self.id).all()]

    def to_dict(self, for_user=None):
        assert isinstance(for_user, int | None)

        d = {
            'id': self.id,
            'nym': self.nym,
            'display_name': self.display_name,
            'profile_image_url': self.twitter_profile_image_url,
            'email': self.email,
            'email_verified': self.email_verified,
            'telegram_username': self.telegram_username,
            'telegram_username_verified': self.telegram_username_verified,
            'twitter_username': self.twitter_username,
            'twitter_username_verified': self.twitter_username_verified,
            'twitter_verification_phrase_sent_at': self.twitter_verification_phrase_sent_at.isoformat() + "Z" if self.twitter_verification_phrase_sent_at else None,
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

        if self.is_moderator:
            d['is_moderator'] = True

        d['badges'] = self.get_badges()

        if for_user == self.id:
            # only ever show these fields to the actual user
            d['contribution_percent'] = self.contribution_percent
            d['xpub'] = self.xpub
            d['xpub_index'] = self.xpub_index

        return d

class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    badge = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(32), nullable=False)
    awarded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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
            'body': f"{buyer.nym} is the winner for {auction.item.title}! {app.config['WWW_BASE_URL']}/auctions/{auction.key}",
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

NOTIFICATION_TYPES = OrderedDict([
    (nt.notification_type, nt) for nt in [
        NewBidNotification(),
        AuctionEndNotification(),
        AuctionEnd10MinNotification(),
        SaleExpiredNotification(),
        PurchaseExpiredNotification(),
        AuctionHasWinnerNotification(),
        AuctionWonNotification(),
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

class TwitterDMNotificationAction(NotificationAction):
    @property
    def action(self):
        return 'TWITTER_DM'

    @property
    def description(self):
        return "Twitter DM"

    def execute(self, user, message):
        from main import get_twitter
        twitter = get_twitter()
        twitter_user = twitter.get_user(user.twitter_username)
        if not twitter_user:
            return False
        return twitter.send_dm(twitter_user['id'], message.body)

NOTIFICATION_ACTIONS = OrderedDict([
    (na.action, na) for na in [IgnoreNotificationAction(), TwitterDMNotificationAction()]
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
            if NOTIFICATION_ACTIONS[action].execute(user, message):
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

class Campaign(XpubMixin, GeneratedKeyMixin, StateMixin, db.Model):
    __tablename__ = 'campaigns'

    REQUIRED_FIELDS = ['xpub', 'name', 'description']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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

    xpub = db.Column(db.String(128), nullable=False)
    xpub_index = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    auctions = db.relationship('Auction', backref='campaign')
    listings = db.relationship('Listing', backref='campaign')

    sales = db.relationship('Sale', backref='campaign', order_by="Sale.requested_at")

    def to_dict(self, for_user=None):
        campaign = {
            'key': self.key,
            'banner_url': self.banner_url,
            'name': self.name,
            'description': self.description,
            'xpub': self.xpub,
            'xpub_index': self.xpub_index,
            'created_at': self.created_at.isoformat() + "Z",
            'is_mine': for_user == self.owner_id,
            'owner_nym': self.owner.nym,
            'owner_display_name': self.owner.display_name,
            'owner_profile_image_url': self.owner.twitter_profile_image_url,
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
        if for_method == 'POST' and 'xpub' in d: # xpub can only be set once, on POST
            k = BTC.parse(d['xpub'])
            if not k:
                raise ValidationError("Invalid XPUB.")
            try:
                first_address = k.subkey(0).subkey(0).address()
            except AttributeError:
                raise ValidationError("Invalid XPUB.")
            validated['xpub'] = d['xpub']
            validated['xpub_index'] = 0
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

    shipping_from = db.Column(db.String(64), nullable=True)
    shipping_domestic_usd = db.Column(db.Float(), nullable=False, default=0)
    shipping_worldwide_usd = db.Column(db.Float(), nullable=False, default=0)

    media = db.relationship('Media', backref='item', foreign_keys='Media.item_id', order_by="Media.index")

    is_hidden = db.Column(db.Boolean, nullable=False, default=False)

    auctions = db.relationship('Auction', backref='item')
    listings = db.relationship('Listing', backref='item')

    sales = db.relationship('Sale', backref='item', order_by="Sale.requested_at")

    @classmethod
    def validate_dict(cls, d, for_method=None):
        validated = {}
        for k in ['title', 'description', 'category', 'shipping_from']:
            if k not in d:
                continue
            length = len(d[k])
            max_length = getattr(Item, k).property.columns[0].type.length
            if length > max_length:
                raise ValidationError(f"Please keep the {k} below {max_length} characters. You are currently at {length}.")
            validated[k] = bleach.clean(d[k])
        for k in ['shipping_domestic_usd', 'shipping_worldwide_usd']:
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

    REQUIRED_FIELDS = ['title', 'description', 'duration_hours', 'starting_bid', 'reserve_bid', 'shipping_domestic_usd', 'shipping_worldwide_usd']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    ########
    # TODO: these should be removed, as they are now duplicated in the Item class!
    seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    title = db.Column(db.String(210), nullable=True)
    description = db.Column(db.String(21000), nullable=True)
    shipping_from = db.Column(db.String(64), nullable=True)
    shipping_estimate_domestic = db.Column(db.String(64), nullable=True)
    shipping_estimate_worldwide = db.Column(db.String(64), nullable=True)
    ########
    ########
    # TODO: these should be removed, as they are now part of Sale!
    contribution_payment_request = db.Column(db.String(512), nullable=True, unique=True, index=True)
    contribution_requested_at = db.Column(db.DateTime, nullable=True)
    contribution_settled_at = db.Column(db.DateTime, nullable=True) # the contribution is settled after the Lightning invoice has been paid
    contribution_amount = db.Column(db.Integer, nullable=True)
    ########

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=False)

    @property
    def owner_id(self):
        return self.item.seller_id

    # this key uniquely identifies the auction. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

    campaign_id = db.Column(db.Integer, db.ForeignKey(Campaign.id), nullable=True)

    # in the case of Twitter-based auctions, start_date is only set after the tweet is published and the auction starts
    start_date = db.Column(db.DateTime, nullable=True)

    @property
    def started(self):
        return self.start_date <= datetime.utcnow() if self.start_date else False

    # duration_hours reflects the initial duration,
    # but the auction can be extended when bids come in close to the end - hence the end_date
    duration_hours = db.Column(db.Float, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)

    @property
    def ended(self):
        return self.end_date < datetime.utcnow() if self.end_date else False

    starting_bid = db.Column(db.Integer, nullable=False)
    reserve_bid = db.Column(db.Integer, nullable=False)

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

    def featured_sort_key(self):
        return len(self.bids)

    @property
    def reserve_bid_reached(self):
        if self.reserve_bid == 0:
            return True
        top_bid = self.get_top_bid()
        return top_bid.amount >= self.reserve_bid if top_bid else False

    def to_dict(self, for_user=None):
        auction = {
            'key': self.key,
            'title': self.item.title,
            'description': self.item.description,
            'category': self.item.category,
            'duration_hours': self.duration_hours,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'started': self.started,
            'end_date': self.end_date.isoformat() + "Z" if self.end_date else None,
            'end_date_extended': self.end_date > self.start_date + timedelta(hours=self.duration_hours) if self.start_date else False,
            'ended': self.ended,
            'starting_bid': self.starting_bid,
            'reserve_bid_reached': self.reserve_bid_reached,
            'shipping_from': self.item.shipping_from,
            'shipping_domestic_usd': self.item.shipping_domestic_usd,
            'shipping_worldwide_usd': self.item.shipping_worldwide_usd,
            'has_winner': self.has_winner,
            'bids': [bid.to_dict(for_user=for_user) for bid in self.bids if bid.settled_at],
            'created_at': self.created_at.isoformat() + "Z",
            'campaign_key': self.campaign.key if self.campaign else None,
            'campaign_name': self.campaign.name if self.campaign else None,
            'is_mine': for_user == self.item.seller_id if for_user else False,
            'seller_nym': self.item.seller.nym,
            'seller_display_name': self.item.seller.display_name,
            'seller_profile_image_url': self.item.seller.twitter_profile_image_url,
            'seller_email': self.item.seller.email,
            'seller_email_verified': self.item.seller.email_verified,
            'seller_telegram_username': self.item.seller.telegram_username,
            'seller_telegram_username_verified': self.item.seller.telegram_username_verified,
            'seller_twitter_username': self.item.seller.twitter_username,
            'seller_twitter_username_verified': self.item.seller.twitter_username_verified,
        }

        auction['bid_thresholds'] = [{'bid_amount_usd': bd['threshold_usd'], 'required_badge': b}
            for b, bd in sorted(app.config['BADGES'].items(), key=lambda i: i[1]['threshold_usd'])]

        if self.item.category == Category.Time.value:
            auction['media'] = [{'index': 0, 'hash': 'TODO', 'url': self.item.seller.twitter_profile_image_url}]
        else:
            auction['media'] = [media.to_dict() for media in self.item.media]

        if for_user == self.owner_id:
            auction['reserve_bid'] = self.reserve_bid

        if for_user:
            # NB: we only return sales for the current user, but for the seller we return all sales
            auction['sales'] = [sale.to_dict()
                for sale in self.item.sales
                if sale.buyer_id == for_user or for_user == self.owner_id]

        if auction['has_winner']:
            winning_bid = [b for b in self.bids if b.id == self.winning_bid_id][0]
            auction['winner_nym'] = winning_bid.buyer.nym
            auction['winner_display_name'] = winning_bid.buyer.display_name
            auction['winner_profile_image_url'] = winning_bid.buyer.twitter_profile_image_url
            auction['winner_email'] = winning_bid.buyer.email
            auction['winner_email_verified'] = winning_bid.buyer.email_verified
            auction['winner_telegram_username'] = winning_bid.buyer.telegram_username
            auction['winner_telegram_username_verified'] = winning_bid.buyer.telegram_username_verified
            auction['winner_twitter_username'] = winning_bid.buyer.twitter_username
            auction['winner_twitter_username_verified'] = winning_bid.buyer.twitter_username_verified

        if for_user is not None:
            user_auction = UserAuction.query.filter_by(user_id=for_user, auction_id=self.id).one_or_none()
            auction['following'] = user_auction.following if user_auction is not None else False
        else:
            auction['following'] = False # TODO: when does this even happen?

        return auction

    @classmethod
    def validate_dict(cls, d, for_method=None):
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
        return validated

class Listing(GeneratedKeyMixin, StateMixin, db.Model):
    __tablename__ = 'listings'

    REQUIRED_FIELDS = ['title', 'description', 'price_usd', 'available_quantity', 'shipping_domestic_usd', 'shipping_worldwide_usd']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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

    def featured_sort_key(self):
        return self.start_date

    def to_dict(self, for_user=None):
        assert isinstance(for_user, int | None)

        listing = {
            'key': self.key,
            'title': self.item.title,
            'description': self.item.description,
            'category': self.item.category,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'started': self.started,
            'ended': self.ended,
            'price_usd': self.price_usd,
            'available_quantity': self.available_quantity,
            'shipping_from': self.item.shipping_from,
            'shipping_domestic_usd': self.item.shipping_domestic_usd,
            'shipping_worldwide_usd': self.item.shipping_worldwide_usd,
            'created_at': self.created_at.isoformat() + "Z",
            'campaign_key': self.campaign.key if self.campaign else None,
            'campaign_name': self.campaign.name if self.campaign else None,
            'is_mine': for_user == self.item.seller_id,
            'seller_nym': self.item.seller.nym,
            'seller_display_name': self.item.seller.display_name,
            'seller_profile_image_url': self.item.seller.twitter_profile_image_url,
            'seller_email': self.item.seller.email,
            'seller_email_verified': self.item.seller.email_verified,
            'seller_telegram_username': self.item.seller.telegram_username,
            'seller_telegram_username_verified': self.item.seller.telegram_username_verified,
            'seller_twitter_username': self.item.seller.twitter_username,
            'seller_twitter_username_verified': self.item.seller.twitter_username_verified,
        }
        if self.item.category == Category.Time.value:
            listing['media'] = [{'index': 0, 'hash': 'TODO', 'url': self.item.seller.twitter_profile_image_url}]
        else:
            listing['media'] = [media.to_dict() for media in self.item.media]

        if for_user:
            # NB: we only return sales for the current user, so that the UI can know the sales were settled
            # sales for other users should be kept private or eventually shown to the seller only!
            listing['sales'] = [sale.to_dict() for sale in self.item.sales if sale.buyer_id == for_user]

        return listing

    @classmethod
    def validate_dict(cls, d, for_method=None):
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

    # TODO: remove this!
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=True)

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
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime) # a bid is settled after the Lightning invoice has been paid

    amount = db.Column(db.Integer, nullable=False)

    # payment_request identifies the Lightning invoice
    payment_request = db.Column(db.String(512), nullable=True, unique=True, index=True)

    def to_dict(self, for_user=None):
        bid = {
            'amount': self.amount,
            'buyer_nym': self.buyer.nym,
            'buyer_display_name': self.buyer.display_name,
            'buyer_profile_image_url': self.buyer.twitter_profile_image_url,
            'buyer_email': self.buyer.email,
            'buyer_email_verified': self.buyer.email_verified,
            'buyer_telegram_username': self.buyer.telegram_username,
            'buyer_telegram_username_verified': self.buyer.telegram_username_verified,
            'buyer_twitter_username': self.buyer.twitter_username,
            'buyer_twitter_username_verified': self.buyer.twitter_username_verified,
            'settled_at': (self.settled_at.isoformat() + "Z" if self.settled_at else None),
            'is_winning_bid': self.id == self.auction.winning_bid_id,
        }
        if for_user == self.buyer_id:
            # if the buyer that placed this bid is looking, we can share the payment_request with him so he knows the transaction was settled
            bid['payment_request'] = self.payment_request
        return bid

class SaleState(Enum):
    OLD = -1 # old sales, from before we used to settle on-chain
    REQUESTED = 0
    CONTRIBUTION_SETTLED = 1
    TX_DETECTED = 2
    TX_CONFIRMED = 3
    EXPIRED = 4

class Sale(db.Model):
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
        else:
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
            'seller_profile_image_url': self.item.seller.twitter_profile_image_url if self.item else None,
            'seller_email': self.item.seller.email if self.item else None,
            'seller_email_verified': self.item.seller.email_verified if self.item else False,
            'seller_telegram_username': self.item.seller.telegram_username if self.item else None,
            'seller_telegram_username_verified': self.item.seller.telegram_username_verified if self.item else False,
            'seller_twitter_username': self.item.seller.twitter_username if self.item else None,
            'seller_twitter_username_verified': self.item.seller.twitter_username_verified if self.item else False,
            'buyer_nym': self.buyer.nym,
            'buyer_display_name': self.buyer.display_name,
            'buyer_profile_image_url': self.buyer.twitter_profile_image_url,
            'buyer_email': self.buyer.email,
            'buyer_email_verified': self.buyer.email_verified,
            'buyer_telegram_username': self.buyer.telegram_username,
            'buyer_telegram_username_verified': self.buyer.telegram_username_verified,
            'buyer_twitter_username': self.buyer.twitter_username,
            'buyer_twitter_username_verified': self.buyer.twitter_username_verified,
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
