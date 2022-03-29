from datetime import datetime
import hashlib
import random
import string

from plebbid.main import app, db

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

class Seller(db.Model):
    __tablename__ = 'sellers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Having access to this key would allow creating, modifying or deleting auctions for the seller using the API.
    # Ideally it is something like a hash of the seller's domain name salted with a unique key known only by the seller (generated when the plugin is installed).
    # A downside of this approach is that if the seller - for example - reinstalls the Wordpress plugin (thus losing access to the unique key),
    # they would lose access to all auctions. This can be solved using a paper backup of this key.
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)

    auctions = db.relationship('Auction', backref='seller', order_by="Auction.id")

class Buyer(db.Model):
    __tablename__ = 'buyers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # This key comes from the user's Lightning wallet when performing a Lightning log in.
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

    bids = db.relationship('Bid', backref='buyer')

class Auction(db.Model):
    __tablename__ = 'auctions'
    __table_args__ = (db.Index('idx_auction_seller_id_short_id', 'seller_id', 'short_id'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    seller_id = db.Column(db.Integer, db.ForeignKey(Seller.id))

    # short_id is unique only within one seller's auctions
    # the purpose of this field is to have a "nice" ID for the auction from the seller's point of view
    # while it *may* be shared with the clients,
    # it isn't of much use to them, since it only makes sense coupled with the seller key
    short_id = db.Column(db.Integer, nullable=False)

    # this key uniquely identifies the auction. It is safe to be shared with anyone.
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)

    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    minimum_bid = db.Column(db.Integer, nullable=False)
    winning_bid_id = db.Column(db.Integer, db.ForeignKey('bids.id'), nullable=True)

    bids = db.relationship('Bid', backref='auction', foreign_keys='Bid.auction_id', order_by='Bid.amount')

    @classmethod
    def generate_key(cls):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(12))

    def to_dict(self, for_seller=None, for_buyer=None):
        auction = {
            'key': self.key,
            'starts_at': self.starts_at.isoformat(),
            'ends_at': self.ends_at.isoformat(),
            'minimum_bid': self.minimum_bid}
        if for_seller == self.seller_id:
            auction['short_id'] = self.short_id
        if for_seller == self.seller_id or self.starts_at <= datetime.utcnow() <= self.ends_at:
            auction['bids'] = [bid.to_dict(for_buyer=for_buyer) for bid in self.bids if bid.settled_at]
        return auction

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id))
    buyer_id = db.Column(db.Integer, db.ForeignKey(Buyer.id))

    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime) # a bid is settled after the Lightning invoice has been paid

    amount = db.Column(db.Integer, nullable=False)

    # payment_request identifies the Lightning invoice
    payment_request = db.Column(db.String(512), nullable=False, unique=True, index=True)

    def to_dict(self, for_buyer=None):
        bid = {
            'amount': self.amount,
            'bidder': self.buyer.public_key}
        if for_buyer == self.buyer_id:
            # if the buyer that placed this bid is looking, we can share the payment_request with him so he knows the transaction was settled
            bid['payment_request'] = self.payment_request
        return bid
