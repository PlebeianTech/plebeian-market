from datetime import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID

from plebbid.main import app, db

class Seller(db.Model):
    __tablename__ = 'sellers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # a hash of the seller's domain name salted with a unique key known only by the seller?
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)

class Buyer(db.Model):
    __tablename__ = 'buyers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registered_at = db.Column(db.DateTime, nullable=False)
    nym = db.Column(db.String(100), unique=True, nullable=False)

    # TODO: not sure yet what this key will be, but probably it will the the linkingKey described in lnurl-auth https://github.com/fiatjaf/lnurl-rfc/blob/master/lnurl-auth.md
    # alternatively, we should maybe move this to a separate table if we want to support multiple authentication methods (email/password, Twitter, ...)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)

class Auction(db.Model):
    __tablename__ = 'auctions'
    __table_args__ = (db.Index('idx_auction_seller_id_short_id', 'seller_id', 'short_id'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey(Seller.id))
    short_id = db.Column(db.Integer, nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    minimum_bid = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'short_id': self.short_id,
            'starts_at': self.starts_at.isoformat(),
            'ends_at': self.ends_at.isoformat(),
            'minimum_bid': self.minimum_bid}

class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer, db.ForeignKey(Auction.id))
    buyer_id = db.Column(db.Integer, db.ForeignKey(Buyer.id))
    requested_at = db.Column(db.DateTime, nullable=False)
    settled_at = db.Column(db.DateTime)
    amount = db.Column(db.Integer, nullable=False)
    payment_request = db.Column(db.String(100), nullable=False, unique=True, index=True)
