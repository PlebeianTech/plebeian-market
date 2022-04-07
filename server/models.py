from datetime import datetime
import dateutil.parser
import hashlib
import random
import string

from server.main import app, db

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

class State(db.Model):
    __tablename__ = 'state'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_settle_index = db.Column(db.Integer, nullable=False)

class LnAuth(db.Model):
    __tablename__ = 'lnauth'

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

    @property
    def public_key(self):
        """
        This is the user's Lightning (public) key, salted (with the site key) and hashed and shortened.
        It is shared with everyone looking at an auction's bidders and can be used to uniquely identify the bidders on the client.
        The salt makes it impossible to identify the same buyer on different sites.
        """

        # TODO: do we want the auction key also part of this? ie. such that the same buyer cannot be identified between different auctions?

        sha = hashlib.sha512()
        sha.update((self.key + app.config['SECRET_KEY']).encode('utf-8'))
        return sha.digest().hex()[:16]

    auctions = db.relationship('Auction', backref='seller', order_by="Auction.starts_at")
    bids = db.relationship('Bid', backref='buyer')

class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    seller_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # this key uniquely identifies the auction. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    minimum_bid = db.Column(db.Integer, nullable=False)
    winning_bid_id = db.Column(db.Integer, db.ForeignKey('bids.id'), nullable=True)

    def __init__(self, **kwargs):
        key = ''.join(random.choice(string.ascii_lowercase) for i in range(12))
        super().__init__(key=key, **kwargs)

    bids = db.relationship('Bid', backref='auction', foreign_keys='Bid.auction_id', order_by='Bid.requested_at')

    def to_dict(self, for_user=None):
        auction = {
            'key': self.key,
            'starts_at': self.starts_at.isoformat() + "Z",
            'ends_at': self.ends_at.isoformat() + "Z",
            'minimum_bid': self.minimum_bid}
        if for_user == self.seller_id or self.starts_at <= datetime.utcnow() <= self.ends_at:
            # showing all bids only to the seller, or during the auction's lifetime
            bids = [bid for bid in self.bids if bid.settled_at]
        elif for_user:
            # otherwise, we show only the buyer's bids
            bids = [bid for bid in self.bids if bid.settled_at and bid.buyer_id == for_user]
        else:
            # if you're not the seller, you have no bids, or you came after the auction ended
            #  => no soup for you!
            bids = []
        auction['bids'] = [bid.to_dict(for_user=for_user) for bid in bids]

        return auction

    def update_from_dict(self, d):
        for k in ['starts_at', 'ends_at']:
            if k not in d:
                continue
            try:
                date = dateutil.parser.isoparse(d[k])
                if date.tzinfo != dateutil.tz.tzutc():
                    raise ValidationError(f"Date must be in UTC: {k}.")
                date = date.replace(tzinfo=None)
            except ValueError:
                raise ValidationError(f"Invalid date: {k}.")
            if date < datetime.utcnow():
                raise ValidationError(f"Date must be in the future: {k}.")
            setattr(self, k, date)
        if 'minimum_bid' in d:
            try:
                minimum_bid = int(d['minimum_bid'])
            except ValueError:
                raise ValidationError("Invalid minimum_bid.")
            self.minimum_bid = minimum_bid

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id))
    buyer_id = db.Column(db.Integer, db.ForeignKey(User.id))

    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime) # a bid is settled after the Lightning invoice has been paid

    amount = db.Column(db.Integer, nullable=False)

    # payment_request identifies the Lightning invoice
    payment_request = db.Column(db.String(512), nullable=False, unique=True, index=True)

    def to_dict(self, for_user=None):
        bid = {
            'amount': self.amount,
            'bidder': self.buyer.public_key}
        if for_user == self.buyer_id:
            # if the buyer that placed this bid is looking, we can share the payment_request with him so he knows the transaction was settled
            bid['payment_request'] = self.payment_request
        return bid
