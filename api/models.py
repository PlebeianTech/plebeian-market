import abc
from base64 import b32encode
from collections import OrderedDict
from datetime import datetime, timedelta
import dateutil.parser
from enum import Enum
import hashlib
from io import BytesIO
import math
from os import urandom
from pycoin.symbols.btc import network as BTC
import random
import string
import bleach
import pyqrcode
import requests

from extensions import db
from main import app
from utils import guess_ext, pick_ext

def store_image(s3, filename, append_hash, original_filename, data):
    if data is None:
        url = original_filename
        response = requests.get(url)
        if response.status_code != 200:
            return None, None
        data = response.content

    sha = hashlib.sha256()
    sha.update(data)
    content_hash = sha.hexdigest()

    ext = pick_ext([guess_ext(data), original_filename.rsplit('.', 1)[-1]])
    filename = f"{filename}_{content_hash}{ext}" if append_hash else f"{filename}{ext}"

    s3.upload(data, filename)

    return s3.get_url_prefix() + s3.get_filename_prefix() + filename, content_hash

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

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

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Lightning log in key
    key = db.Column(db.String(128), unique=True, nullable=False, index=True)

    # ask Pedro about this
    xpub = db.Column(db.String(128), nullable=True)
    xpub_index = db.Column(db.Integer, nullable=True)

    nym = db.Column(db.String(32), unique=True, nullable=True, index=True)

    # TODO: rename to profile_image_url
    twitter_profile_image_url = db.Column(db.String(256), nullable=True)

    stall_banner_url = db.Column(db.String(256), nullable=True)
    stall_name = db.Column(db.String(256), nullable=True)
    stall_description = db.Column(db.String(21000), nullable=True)

    twitter_username = db.Column(db.String(32), unique=True, nullable=True, index=True)
    twitter_username_verified = db.Column(db.Boolean, nullable=False, default=False)
    twitter_username_verification_tweet_id = db.Column(db.String(64), nullable=True)

    @property
    def is_moderator(self):
        return (self.id in app.config['MODERATOR_USER_IDS']) or ('ALL' in app.config['MODERATOR_USER_IDS'])

    contribution_percent = db.Column(db.Float, nullable=True)

    campaigns = db.relationship('Campaign', backref='owner', order_by="desc(Campaign.created_at)")
    items = db.relationship('Item', backref='seller', order_by="desc(Item.created_at)", lazy='dynamic')
    auctions = db.relationship('Auction', backref='seller', order_by="desc(Auction.created_at)", lazy='dynamic')
    bids = db.relationship('Bid', backref='buyer')
    messages = db.relationship('Message', backref='user')

    sales = db.relationship('Sale', backref='buyer')

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
        contribution_amount = int(self.contribution_percent / 100 * for_amount)
        if contribution_amount < app.config['MINIMUM_CONTRIBUTION_AMOUNT']:
            contribution_amount = 0 # probably not worth the fees, at least in the next few years
        return contribution_amount

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

    def to_dict(self, for_user=None):
        assert isinstance(for_user, int | None)

        d = {
            'id': self.id,
            'nym': self.nym,
            'profile_image_url': self.twitter_profile_image_url,
            'twitter_username': self.twitter_username,
            'twitter_username_verified': self.twitter_username_verified,
            'stall_banner_url': self.stall_banner_url,
            'stall_name': self.stall_name,
            'stall_description': self.stall_description,
            'has_items': len(self.items.all()) > 0,
            'has_auctions': sum(len(i.auctions) for i in self.items.all()) > 0,
            'has_listings': sum(len(i.listings) for i in self.items.all()) > 0,
        }

        if self.is_moderator:
            d['is_moderator'] = True

        if for_user == self.id:
            # only ever show these fields to the actual user
            d['contribution_percent'] = self.contribution_percent
            d['xpub'] = self.xpub
            d['xpub_index'] = self.xpub_index
            if self.twitter_username_verification_tweet_id:
                d['twitter_username_verification_tweet'] = f"https://twitter.com/{app.config['TWITTER_USER']}/status/{self.twitter_username_verification_tweet_id}"
            else:
                d['twitter_username_verification_tweet'] = None

        return d

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
    @abc.abstractmethod
    def default_action(self):
        pass

    @abc.abstractmethod
    def get_message_args(self, user, auction, bid):
        pass

class AuctionEndNotification(Notification):
    @property
    def notification_type(self):
        return "AUCTION_END"

    @property
    def description(self):
        return "Auction ended"

    @property
    def default_action(self):
        return 'NONE'

    def get_message_args(self, user, auction, bid):
        # NB: "bid is None" means this notification refers to an auction
        if bid is None and auction.ended:
            return {
                'user_id': user.id,
                'key': f"{self.notification_type}_{auction.id}",
                'body': f"Auction {auction.title} ended!",
            }

class AuctionEnd10MinNotification(Notification):
    @property
    def notification_type(self):
        return "AUCTION_END_10MIN"

    @property
    def description(self):
        return "Auction ending in 10 minutes"

    @property
    def default_action(self):
        return 'NONE'

    def get_message_args(self, user, auction, bid):
        # NB: "bid is None" means this notification refers to an auction
        if bid is None and auction.end_date <= (datetime.utcnow() + timedelta(minutes=10)):
            return {
                'user_id': user.id,
                'key': f"{self.notification_type}_{auction.id}",
                'body': f"Auction {auction.title} ending in less than 10 minutes!",
            }

class NewBidNotification(Notification):
    @property
    def notification_type(self):
        return "NEW_BID"

    @property
    def description(self):
        return "New bid"

    @property
    def default_action(self):
        return 'NONE'

    def get_message_args(self, user, auction, bid):
        if bid is not None and bid.buyer_id != user.id: # the bidder should not be notified
            return {
                'user_id': user.id,
                'key': f"{self.notification_type}_{auction.id}_{bid.id}",
                'body': f"New bid on {auction.title} by {bid.buyer.twitter_username}: {bid.amount} sats!",
            }

NOTIFICATION_TYPES = OrderedDict([
    (nt.notification_type, nt) for nt in [NewBidNotification(), AuctionEndNotification(), AuctionEnd10MinNotification()]
])

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
    (na.action, na) for na in [IgnoreNotificationAction(), TwitterDMNotificationAction(), InternalNotificationAction()]
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

    def to_dict(self):
        return {
            'key': self.key,
            'created_at': self.created_at.isoformat() + "Z",
            'body': self.body,
            'notified_via': self.notified_via,
        }

def hash_create(length):
    return b32encode(urandom(length)).decode("ascii").replace("=", "")

def generate_key(cls, count):
    # code taken from https://github.com/supakeen/pinnwand and adapted

    # TODO: while this works great for now, it would be nice to have it be somehow derived from the User key
    # - perhaps some hash(user key + index), where index represents a User's Auction index (1, 2, 3...)
    # The benefit (of that) would be that a user could then potentially have auctions which don't necessary have an underlying Auction record,
    # in the same way in which an XPUB can derive "addresses" that don't represent an actual UTXO?

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
    key = hash_create(necessary)

    while cls.query.filter_by(key=key).one_or_none():
        app.logger.debug("generate_key: triggered a collision")
        if tries > 10:
            raise RuntimeError("We exceeded our retry quota on a collision.")
        tries += 1
        key = hash_create(necessary)

    return key

class FilterStateMixin:
    def matches_filter(self, for_user_id, request_filter):
        seller_id = self.item.seller_id if self.item else self.seller_id
        is_seller = for_user_id == seller_id
        match request_filter:
            case 'not-new':
                return self.started
            case 'new':
                if is_seller:
                    return not self.started and not self.ended
                else:
                    return False
            case None:
                if is_seller:
                    return True
                else:
                    return self.started and not self.ended

class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    key = db.Column(db.String(24), unique=True, nullable=False, index=True)

    title = db.Column(db.String(210), nullable=False)
    description = db.Column(db.String(21000), nullable=False)

    start_date = db.Column(db.DateTime, nullable=True)

    @property
    def started(self):
        return self.start_date <= datetime.utcnow() if self.start_date else False

    # TODO: we should probably remove this and define "ended" as having no active auctions/listings
    end_date = db.Column(db.DateTime, nullable=True)

    @property
    def ended(self):
        return self.end_date < datetime.utcnow() if self.end_date else False

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self, for_user=None):
        campaign = {
            'key': self.key,
            'title': self.title,
            'description': self.description,
            'started': self.started,
            'ended': self.ended,
            'created_at': self.created_at.isoformat() + "Z",
            'owner_nym': self.owner.nym,
            'owner_profile_image_url': self.owner.twitter_profile_image_url,
            'owner_twitter_username': self.owner.twitter_username,
            'owner_twitter_username_verified': self.owner.twitter_username_verified,
        }

        return campaign

    @classmethod
    def generate_key(cls, count):
        return generate_key(cls, count)

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        for k in ['title', 'description']:
            if k not in d:
                continue
            length = len(d[k])
            max_length = getattr(Campaign, k).property.columns[0].type.length
            if length > max_length:
                raise ValidationError(f"Please keep the {k} below {max_length} characters. You are currently at {length}.")
            validated[k] = d[k]
        return validated

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    title = db.Column(db.String(210), nullable=False)
    description = db.Column(db.String(21000), nullable=False)

    shipping_from = db.Column(db.String(64), nullable=True)
    shipping_domestic_usd = db.Column(db.Float(), nullable=False, default=0)
    shipping_worldwide_usd = db.Column(db.Float(), nullable=False, default=0)

    media = db.relationship('Media', backref='item', foreign_keys='Media.item_id', order_by="Media.index")

    is_hidden = db.Column(db.Boolean, nullable=False, default=False)

    auctions = db.relationship('Auction', backref='item')
    listings = db.relationship('Listing', backref='item')

    sales = db.relationship('Sale', backref='item', order_by="Sale.requested_at")

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        for k in ['title', 'description', 'shipping_from']:
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

class Auction(FilterStateMixin, db.Model):
    __tablename__ = 'auctions'

    REQUIRED_FIELDS = ['title', 'description', 'duration_hours', 'starting_bid', 'reserve_bid', 'shipping_domestic_usd', 'shipping_worldwide_usd']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    ########
    # TODO: these should be removed, as they are now duplicated in the Item class,
    # but for now we keep them around until we migrate the old Auction data to Item
    # and make sure we didn't break something.
    seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    title = db.Column(db.String(210), nullable=False)
    description = db.Column(db.String(21000), nullable=False)
    shipping_from = db.Column(db.String(64), nullable=True)
    shipping_estimate_domestic = db.Column(db.String(64), nullable=True)
    shipping_estimate_worldwide = db.Column(db.String(64), nullable=True)
    media = db.relationship('Media', backref='auction', foreign_keys='Media.auction_id')
    ########
    # TODO: these should be removed, as they are now part of Sale,
    # but we should first generate Sales for old auctions
    contribution_payment_request = db.Column(db.String(512), nullable=True, unique=True, index=True)
    contribution_requested_at = db.Column(db.DateTime, nullable=True)
    contribution_settled_at = db.Column(db.DateTime, nullable=True) # the contribution is settled after the Lightning invoice has been paid
    contribution_amount = db.Column(db.Integer, nullable=True)
    ########
    # TODO: this should eventually become non-nullable
    # after we will have created Item records for all old auctions!
    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=True)
    ########

    # this key uniquely identifies the auction. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

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
    media = db.relationship('Media', backref='auction', foreign_keys='Media.auction_id')

    user_auctions = db.relationship('UserAuction', cascade="all,delete", backref='auction')

    sales = db.relationship('Sale', backref='auction')

    def get_top_bid(self):
        return max((bid for bid in self.bids if bid.settled_at), default=None, key=lambda bid: bid.amount)

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
            'title': self.item.title if self.item else self.title,
            'description': self.item.description if self.item else self.description,
            'duration_hours': self.duration_hours,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'started': self.started,
            'end_date': self.end_date.isoformat() + "Z" if self.end_date else None,
            'end_date_extended': self.end_date > self.start_date + timedelta(hours=self.duration_hours) if self.start_date else False,
            'ended': self.ended,
            'starting_bid': self.starting_bid,
            'reserve_bid_reached': self.reserve_bid_reached,
            'shipping_from': self.item.shipping_from if self.item else self.shipping_from,
            'shipping_domestic_usd': self.item.shipping_domestic_usd if self.item else 0,
            'shipping_worldwide_usd': self.item.shipping_worldwide_usd if self.item else 0,
            'has_winner': self.has_winner,
            'bids': [bid.to_dict(for_user=for_user) for bid in self.bids if bid.settled_at],
            'media': [media.to_dict() for media in self.media or (self.item.media if self.item else [])],
            'created_at': self.created_at.isoformat() + "Z",
            'is_mine': for_user == self.seller_id,
            'seller_nym': self.item.seller.nym if self.item else self.seller.nym,
            'seller_profile_image_url': self.item.seller.twitter_profile_image_url if self.item else self.seller.twitter_profile_image_url,
            'seller_twitter_username': self.item.seller.twitter_username if self.item else self.seller.twitter_username,
            'seller_twitter_username_verified': self.item.seller.twitter_username_verified if self.item else self.seller.twitter_username_verified,
        }

        if for_user == self.seller_id:
            auction['reserve_bid'] = self.reserve_bid

        if for_user:
            # NB: we only return sales for the current user, so that the UI can know the sales were settled
            # sales for other users should be kept private or eventually shown to the seller only!
            auction['sales'] = [sale.to_dict() for sale in (self.item.sales if self.item else []) if sale.buyer_id == for_user]

        if auction['has_winner']:
            winning_bid = [b for b in self.bids if b.id == self.winning_bid_id][0]
            auction['winner_nym'] = winning_bid.buyer.nym
            auction['winner_profile_image_url'] = winning_bid.buyer.twitter_profile_image_url
            auction['winner_twitter_username'] = winning_bid.buyer.twitter_username
            auction['winner_twitter_username_verified'] = winning_bid.buyer.twitter_username_verified

        if for_user is not None:
            user_auction = UserAuction.query.filter_by(user_id=for_user, auction_id=self.id).one_or_none()
            auction['following'] = user_auction.following if user_auction is not None else False
        else:
            auction['following'] = False # TODO: when does this even happen?

        return auction

    @classmethod
    def generate_key(cls, count):
        return generate_key(cls, count)

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        # TODO: remove this after the columns have been removed!
        ########
        for k in ['title', 'description']:
            if k not in d:
                continue
            length = len(d[k])
            max_length = getattr(Auction, k).property.columns[0].type.length
            if length > max_length:
                raise ValidationError(f"Please keep the {k} below {max_length} characters. You are currently at {length}.")
            validated[k] = bleach.clean(d[k])
        ########
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

    def ensure_item(self):
        # TODO: this method should be removed after all existing auctions have been modified to point to items
        if not self.item:
            item = Item(
                seller_id=self.seller_id,
                created_at=self.created_at,
                title=self.title, description=self.description,
                shipping_from=self.shipping_from)
            db.session.add(item)
            db.session.commit()
            self.item_id = item.id
            for media in self.media:
                media.item_id = item.id
            db.session.commit()
            app.logger.warning(f"Created item for Auction {self.id}!")

class Listing(FilterStateMixin, db.Model):
    __tablename__ = 'listings'

    REQUIRED_FIELDS = ['title', 'description', 'price_usd', 'available_quantity', 'shipping_domestic_usd', 'shipping_worldwide_usd']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=False)

    # this key uniquely identifies the listing. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

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

    sales = db.relationship('Sale', backref='listing')

    def featured_sort_key(self):
        return self.start_date

    def to_dict(self, for_user=None):
        assert isinstance(for_user, int | None)

        listing = {
            'key': self.key,
            'title': self.item.title,
            'description': self.item.description,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'started': self.started,
            'ended': self.ended,
            'price_usd': self.price_usd,
            'available_quantity': self.available_quantity,
            'shipping_from': self.item.shipping_from,
            'shipping_domestic_usd': self.item.shipping_domestic_usd,
            'shipping_worldwide_usd': self.item.shipping_worldwide_usd,
            'media': [media.to_dict() for media in self.item.media],
            'created_at': self.created_at.isoformat() + "Z",
            'is_mine': for_user == self.item.seller_id,
            'seller_nym': self.item.seller.nym,
            'seller_profile_image_url': self.item.seller.twitter_profile_image_url,
            'seller_twitter_username': self.item.seller.twitter_username,
            'seller_twitter_username_verified': self.item.seller.twitter_username_verified,
        }

        if for_user:
            # NB: we only return sales for the current user, so that the UI can know the sales were settled
            # sales for other users should be kept private or eventually shown to the seller only!
            listing['sales'] = [sale.to_dict() for sale in self.item.sales if sale.buyer_id == for_user]

        return listing

    @classmethod
    def generate_key(cls, count):
        return generate_key(cls, count)

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
        for k in ['start_date']:
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
        return validated

class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # TODO: this should eventually be dropped after we use only the link in Item
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=True)

    # TODO: this should be set to nullable=False after we drop auction_id
    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=True)

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
    payment_request = db.Column(db.String(512), nullable=False, unique=True, index=True)

    def to_dict(self, for_user=None):
        bid = {
            'amount': self.amount,
            'buyer_nym': self.buyer.nym,
            'buyer_profile_image_url': self.buyer.twitter_profile_image_url,
            'buyer_twitter_username': self.buyer.twitter_username,
            'buyer_twitter_username_verified': self.buyer.twitter_username_verified,
            'settled_at': (self.settled_at.isoformat() + "Z" if self.settled_at else None)}
        if for_user == self.buyer_id:
            # if the buyer that placed this bid is looking, we can share the payment_request with him so he knows the transaction was settled
            bid['payment_request'] = self.payment_request
        return bid

class SaleState(Enum):
    REQUESTED = 0
    CONTRIBUTION_SETTLED = 1
    TX_DETECTED = 2
    TX_CONFIRMED = 3
    EXPIRED = 4

class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    item_id = db.Column(db.Integer, db.ForeignKey(Item.id), nullable=False)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=True)
    listing_id = db.Column(db.Integer, db.ForeignKey(Listing.id), nullable=True)

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

    amount = db.Column(db.Integer, nullable=False) # amount to be paid to the seller (total amount minus contribution) *not* including shipping
    shipping_domestic = db.Column(db.Integer, nullable=False)
    shipping_worldwide = db.Column(db.Integer, nullable=False)

    # the Lightning invoice for the contribution
    contribution_amount = db.Column(db.Integer, nullable=False)
    contribution_payment_request = db.Column(db.String(512), nullable=True, unique=True, index=True)
    contribution_settled_at = db.Column(db.DateTime, nullable=True) # this is NULL initially, and gets set after the contribution has been received

    def to_dict(self):
        sale = {
            'item_title': self.item.title,
            'state': SaleState(self.state).name,
            'price_usd': self.price_usd,
            'price': self.price,
            'quantity': self.quantity,
            'amount': self.amount,
            'shipping_domestic': self.shipping_domestic,
            'shipping_worldwide': self.shipping_worldwide,
            'seller_nym': self.item.seller.nym,
            'seller_profile_image_url': self.item.seller.twitter_profile_image_url,
            'seller_twitter_username': self.item.seller.twitter_username,
            'seller_twitter_username_verified': self.item.seller.twitter_username_verified,
            'buyer_nym': self.buyer.nym,
            'buyer_profile_image_url': self.buyer.twitter_profile_image_url,
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

        if self.state == SaleState.REQUESTED.value:
            contribution_payment_qr = BytesIO()
            pyqrcode.create(self.contribution_payment_request).svg(contribution_payment_qr, omithw=True, scale=4)
            sale['contribution_payment_qr'] = contribution_payment_qr.getvalue().decode('utf-8')
        elif self.state == SaleState.CONTRIBUTION_SETTLED.value:
            address_qr = BytesIO()
            pyqrcode.create(self.address).svg(address_qr, omithw=True, scale=4)
            sale['address_qr'] = address_qr.getvalue().decode('utf-8')

        return sale

class UserAuction(db.Model):
    __tablename__ = 'user_auctions'

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=False, primary_key=True)

    following = db.Column(db.Boolean, nullable=False)
