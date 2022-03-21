from datetime import datetime
import random
import string

from plebbid.main import app, db

class Seller(db.Model):
    __tablename__ = 'sellers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # a hash of the seller's domain name salted with a unique key known only by the seller?
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)

    auctions = db.relationship('Auction', backref='seller', order_by="Auction.id")

class Buyer(db.Model):
    __tablename__ = 'buyers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    key = db.Column(db.String(100), unique=True, nullable=False, index=True)

    bids = db.relationship('Bid', backref='buyer')

class Auction(db.Model):
    __tablename__ = 'auctions'
    __table_args__ = (db.Index('idx_auction_seller_id_short_id', 'seller_id', 'short_id'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(12), unique=True, nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey(Seller.id))
    short_id = db.Column(db.Integer, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    minimum_bid = db.Column(db.Integer, nullable=False)
    winning_bid_id = db.Column(db.Integer, db.ForeignKey('bids.id'), nullable=True)

    bids = db.relationship('Bid', backref='auction', foreign_keys='Bid.auction_id', order_by='Bid.amount')

    @classmethod
    def generate_key(cls):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(12))

    def to_dict(self):
        include_bids = self.starts_at <= datetime.utcnow() <= self.ends_at
        auction = {
            'short_id': self.short_id,
            'key': self.key,
            'starts_at': self.starts_at.isoformat(),
            'ends_at': self.ends_at.isoformat(),
            'minimum_bid': self.minimum_bid}
        if include_bids:
            auction['bids'] = [bid.to_dict() for bid in self.bids if bid.settled_at]
        return auction

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id))
    buyer_id = db.Column(db.Integer, db.ForeignKey(Buyer.id))
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime)
    amount = db.Column(db.Integer, nullable=False)
    payment_request = db.Column(db.String(100), nullable=False, unique=True, index=True)

    def to_dict(self):
        return {
            'amount': self.amount,
            'bidder': self.buyer.key} # TODO: do not return the actual key here, but rather hash & salt it
