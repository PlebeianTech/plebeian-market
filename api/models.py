from base64 import b32encode
from datetime import datetime, timedelta
import dateutil.parser
import hashlib
from io import BytesIO
import math
from os import urandom
import random
import string

import magic
import pyqrcode
import requests

from extensions import db
from main import app

def fetch_image(url, s3, filename):
    response = requests.get(url)
    if response.status_code != 200:
        return None

    original_ext = url.rsplit('.', 1)[-1]
    guessed_ext = magic.Magic(extension=True).from_buffer(response.content).split("/")[0]
    for e in [guessed_ext, original_ext]:
        if e.isalnum() and len(e) <= 5:
            ext = f".{e}"
            break
    else:
        ext = ""

    filename = f"{filename}{ext}"

    s3.upload(response.content, filename)

    return s3.get_url_prefix() + s3.get_filename_prefix() + filename

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class State(db.Model):
    __tablename__ = 'state'

    LAST_SETTLE_INDEX = 'LAST_SETTLE_INDEX'

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

    # can't set this for now, but should be useful in the future
    nym = db.Column(db.String(32), unique=True, nullable=True, index=True)

    twitter_username = db.Column(db.String(32), unique=True, nullable=True, index=True)
    twitter_profile_image_url = db.Column(db.String(256), nullable=True)
    twitter_username_verified = db.Column(db.Boolean, nullable=False, default=False)
    twitter_username_verification_tweet_id = db.Column(db.String(64), nullable=True)

    @property
    def is_moderator(self):
        return self.id in app.config['MODERATOR_USER_IDS']

    contribution_percent = db.Column(db.Float, nullable=True)

    auctions = db.relationship('Auction', backref='seller', order_by="desc(Auction.created_at)")
    bids = db.relationship('Bid', backref='buyer')

    def fetch_twitter_profile_image(self, s3):
        url = fetch_image(self.twitter_profile_image_url, s3, f"user_{self.id}_twitter_profile_image")
        if not url:
            return False
        self.twitter_profile_image_url = url
        return True

    def to_dict(self):
        d = {
            'nym': self.nym,
            'twitter_username': self.twitter_username,
            'twitter_profile_image_url': self.twitter_profile_image_url,
            'twitter_username_verified': self.twitter_username_verified,
            'twitter_username_verification_tweet': f"https://twitter.com/{app.config['TWITTER_USER']}/status/{self.twitter_username_verification_tweet_id}",
            'contribution_percent': self.contribution_percent,
            'has_auctions': len(self.auctions) > 0,
            'has_bids': len(self.bids) > 0}
        if self.is_moderator:
            d['is_moderator'] = True
        return d

def hash_create(length):
    return b32encode(urandom(length)).decode("ascii").replace("=", "")

class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # this key uniquely identifies the auction. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

    # the title *might* eventually become nullable, for the case of WP auctions
    # (the auction title in that case would be the post title)
    title = db.Column(db.String(210), nullable=False)

    description = db.Column(db.String(2100), nullable=False)

    # in the case of Twitter auctions, start_date is only set after the tweet is published and the auction starts
    start_date = db.Column(db.DateTime, nullable=True)

    # duration_hours reflects the initial duration,
    # but the auction can be extended when bids come in close to the end - hence the end_date
    duration_hours = db.Column(db.Float, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)

    starting_bid = db.Column(db.Integer, nullable=False)
    reserve_bid = db.Column(db.Integer, nullable=False)
    instant_buy_price = db.Column(db.Integer, nullable=True)

    shipping_from = db.Column(db.String(64), nullable=True)

    twitter_id = db.Column(db.String(32), nullable=True)

    is_featured = db.Column(db.Boolean, nullable=True)

    # this identifies the Lightning invoice of the contribution payment
    contribution_payment_request = db.Column(db.String(512), nullable=True, unique=True, index=True)

    contribution_requested_at = db.Column(db.DateTime, nullable=True)
    contribution_settled_at = db.Column(db.DateTime, nullable=True) # the contribution is settled after the Lightning invoice has been paid
    contribution_amount = db.Column(db.Integer, nullable=True)

    winning_bid_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    bids = db.relationship('Bid', backref='auction', foreign_keys='Bid.auction_id', order_by='desc(Bid.requested_at)')
    media = db.relationship('Media', backref='auction', foreign_keys='Media.auction_id')

    @property
    def started(self):
        return self.start_date <= datetime.utcnow() if self.start_date else False

    @property
    def ended(self):
        return self.end_date < datetime.utcnow() if self.end_date else False

    def get_top_bid(self):
        return max((bid for bid in self.bids if bid.settled_at), default=None, key=lambda bid: bid.amount)

    @property
    def reserve_bid_reached(self):
        top_bid = self.get_top_bid()
        return top_bid.amount >= self.reserve_bid if top_bid else False

    @property
    def instant_buy(self):
        return self.instant_buy_price is not None

    def to_dict(self, for_user=None):
        auction = {
            'key': self.key,
            'title': self.title,
            'description': self.description,
            'duration_hours': self.duration_hours,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'started': self.started,
            'end_date': self.end_date.isoformat() + "Z" if self.end_date else None,
            'end_date_extended': self.end_date > (self.start_date + timedelta(hours=self.duration_hours)) if (self.start_date and not self.instant_buy) else False,
            'ended': self.ended,
            'starting_bid': self.starting_bid,
            'instant_buy_price': self.instant_buy_price,
            'reserve_bid_reached': self.reserve_bid_reached,
            'shipping_from': self.shipping_from,
            'bids': [bid.to_dict(for_user=for_user) for bid in self.bids if bid.settled_at],
            'media': [{'url': media.url, 'twitter_media_key': media.twitter_media_key} for media in self.media],
            'created_at': self.created_at.isoformat() + "Z",
            'is_mine': for_user == self.seller_id,
            'seller_twitter_username': self.seller.twitter_username,
            'seller_twitter_username_verified': self.seller.twitter_username_verified,
            'seller_twitter_profile_image_url': self.seller.twitter_profile_image_url,
        }

        if for_user == self.seller_id:
            auction['reserve_bid'] = self.reserve_bid

        if self.contribution_amount is not None:
            top_bid = self.get_top_bid() # TODO: should this be based on the winning bid rather than the top bid *if* the contribution was already settled? in case the top bid somehow never becomes the winning bid?
            auction['contribution_amount'] = self.contribution_amount
            auction['remaining_amount'] = top_bid.amount - self.contribution_amount

        if self.winning_bid_id is not None:
            assert self.contribution_settled_at is not None # settle-bids should set both contribution_settled_at and winning_bid_id at the same time!
            auction['has_winner'] = True
            winning_bid = [b for b in self.bids if b.id == self.winning_bid_id][0]
            if for_user == winning_bid.buyer_id and for_user != self.seller_id: # NB: the seller should not normally win the auction (or even bid), but it happens often during testing
                auction['is_won'] = True
            else:
                if for_user and for_user != winning_bid.buyer_id:
                    auction['is_lost'] = True
                auction['winner_twitter_username'] = winning_bid.buyer.twitter_username
                auction['winner_twitter_username_verified'] = winning_bid.buyer.twitter_username_verified
                auction['winner_twitter_profile_image_url'] = winning_bid.buyer.twitter_profile_image_url
        elif self.ended:
            top_bid = self.get_top_bid()
            if top_bid and self.contribution_payment_request is not None:
                if for_user == top_bid.buyer_id:
                    assert self.contribution_amount is not None # this must be set at the same time as contribution_payment_request
                    auction['needs_contribution'] = True
                    auction['contribution_percent'] = self.seller.contribution_percent
                    auction['contribution_payment_request'] = self.contribution_payment_request
                    qr = BytesIO()
                    pyqrcode.create(self.contribution_payment_request).svg(qr, omithw=True, scale=4)
                    auction['contribution_qr'] = qr.getvalue().decode('utf-8')
                elif for_user == self.seller_id:
                    auction['wait_contribution'] = True

        return auction

    @classmethod
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

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        for k in ['title', 'description', 'shipping_from']:
            if k not in d:
                continue
            length = len(d[k])
            max_length = getattr(Auction, k).property.columns[0].type.length
            if length > max_length:
                raise ValidationError(f"Please keep the {k} below {max_length} characters. You are currently at {length}.")
            validated[k] = d[k]
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
        for k in ['starting_bid', 'reserve_bid', 'instant_buy_price']:
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
        for k in ['is_featured']:
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
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=False)
    twitter_media_key = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(256), nullable=False)

    def fetch(self, s3, filename):
        url = fetch_image(self.url, s3, filename)
        if not url:
            return False
        self.url = url
        return True

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
            'twitter_username': self.buyer.twitter_username,
            'twitter_profile_image_url': self.buyer.twitter_profile_image_url,
            'twitter_username_verified': self.buyer.twitter_username_verified,
            'settled_at': (self.settled_at.isoformat() + "Z" if self.settled_at else None)}
        if for_user == self.buyer_id:
            # if the buyer that placed this bid is looking, we can share the payment_request with him so he knows the transaction was settled
            bid['payment_request'] = self.payment_request
        return bid
