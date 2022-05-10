from datetime import datetime, timedelta
import dateutil.parser
import hashlib
import random
import string

from extensions import db
from main import app

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
    twitter_username_verified = db.Column(db.Boolean, nullable=False, default=False)

    contribution_percent = db.Column(db.Integer, nullable=True)

    auctions = db.relationship('Auction', backref='seller', order_by="desc(Auction.start_date), Auction.key")
    bids = db.relationship('Bid', backref='buyer')

    def to_dict(self):
        return {
            'nym': self.nym,
            'twitter_username': self.twitter_username,
            'twitter_username_verified': self.twitter_username_verified,
            'contribution_percent': self.contribution_percent,
            'has_auctions': len(self.auctions) > 0,
            'has_bids': len(self.bids) > 0}

class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    seller_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # this key uniquely identifies the auction. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

    # the title *might* eventually become nullable, for the case of WP auctions
    # (the auction title in that case would be the post title)
    title = db.Column(db.String(32), nullable=False)

    description = db.Column(db.String(512), nullable=False)

    # in the case of Twitter auctions, start_date is only set after the tweet is published and the auction starts
    start_date = db.Column(db.DateTime, nullable=True)

    # duration_hours reflects the initial duration,
    # but the auction can be extended when bids come in close to the end - hence the end_date
    duration_hours = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)

    starting_bid = db.Column(db.Integer, nullable=False)
    reserve_bid = db.Column(db.Integer, nullable=False)

    twitter_id = db.Column(db.String(32), nullable=True)

    winning_bid_id = db.Column(db.Integer, nullable=True)

    canceled = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):

        # TODO: while this works great for now, it would be nice to have it be somehow derived from the User key
        # - perhaps some hash(user key + index), where index represents a User's Auction index (1, 2, 3...)
        # The benefit (of that) would be that a user could then potentially have auctions which don't necessary have an underlying Auction record,
        # in the same way in which an XPUB can derive "addresses" that don't represent an actual UTXO.
        key = ''.join(random.choice(string.ascii_lowercase) for i in range(12))

        super().__init__(key=key, **kwargs)

    bids = db.relationship('Bid', backref='auction', foreign_keys='Bid.auction_id', order_by='desc(Bid.requested_at)')
    media = db.relationship('Media', backref='auction', foreign_keys='Media.auction_id')

    def to_dict(self, for_user=None):
        auction = {
            'key': self.key,
            'title': self.title,
            'description': self.description,
            'duration_hours': self.duration_hours,
            'start_date': self.start_date.isoformat() + "Z" if self.start_date else None,
            'end_date': self.end_date.isoformat() + "Z" if self.end_date else None,
            'canceled': self.canceled,
            'starting_bid': self.starting_bid,
            'bids': [bid.to_dict(for_user=for_user) for bid in self.bids if bid.settled_at],
            'media': [{'url': media.url, 'twitter_media_key': media.twitter_media_key} for media in self.media]
        }
        if for_user == self.seller_id:
            auction['reserve_bid'] = self.reserve_bid

        return auction

    @classmethod
    def validate_dict(cls, d):
        validated = {}
        for k in ['title', 'description']:
            if k not in d:
                continue
            # TODO: validate length?
            validated[k] = d[k]
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
        for k in ['duration_hours', 'starting_bid', 'reserve_bid']:
            if k not in d:
                continue
            try:
                validated[k] = int(d[k])
            except (ValueError, TypeError):
                raise ValidationError(f"{k.replace('_', ' ')} is invalid.".capitalize())
        if 'start_date' in validated and 'duration_hours' in validated:
            validated['end_date'] = validated['start_date'] + timedelta(hours=validated['duration_hours'])
        return validated

class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id), nullable=False)
    twitter_media_key = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(256), nullable=False)

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
            'twitter_username_verified': self.buyer.twitter_username_verified,
            'settled_at': (self.settled_at.isoformat() + "Z" if self.settled_at else None)}
        if for_user == self.buyer_id:
            # if the buyer that placed this bid is looking, we can share the payment_request with him so he knows the transaction was settled
            bid['payment_request'] = self.payment_request
        return bid
