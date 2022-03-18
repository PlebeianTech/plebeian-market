import os

import dateutil.parser
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from plebbid import models as m
from plebbid.main import app, db

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/sellers', methods=['POST'])
def add_seller():
    try:
        db.session.add(m.Seller(key=request.form['key']))
        db.session.commit()
        return jsonify({'ok': True})
    except IntegrityError:
        return jsonify({'message': "Seller already registered."}), 400

@api_blueprint.route('/sellers/<string:key>/auctions', methods=['GET', 'POST'])
def auctions(key):
    seller = m.Seller.query.filter_by(key=key).first_or_404()
    if request.method == 'GET':
        auctions = m.Auction.query.filter_by(seller_id=seller.id).all()
        return jsonify({'ok': True, 'auctions': [a.to_dict() for a in auctions]})
    else:
        for k in ['starts_at', 'ends_at', 'minimum_bid']:
            if k not in request.form:
                return jsonify({'message': "Missing key %s" % k}), 400

        max_short_id = db.session.query(db.func.max(m.Auction.short_id)).filter(m.Auction.seller_id == seller.id).scalar()

        short_id = max_short_id + 1 if max_short_id else 1
        auction = m.Auction(key=os.urandom(12).hex(),
            seller_id=seller.id,
            short_id=short_id,
            starts_at=dateutil.parser.isoparse(request.form['starts_at']),
            ends_at=dateutil.parser.isoparse(request.form['ends_at']),
            minimum_bid=request.form['minimum_bid'])
        db.session.add(auction)
        db.session.commit()
        return jsonify({'ok': True, 'short_id': short_id})

@api_blueprint.route('/sellers/<string:key>/auctions/<int:short_id>', methods=['DELETE'])
def delete_auction(key, short_id):
    seller = m.Seller.query.filter_by(key=key).first_or_404()
    auction = m.Auction.query.filter_by(seller_id=seller.id, short_id=short_id).first_or_404()
    db.session.delete(auction)
    db.session.commit()
    return jsonify({'ok': True})

@api_blueprint.route('/auctions/<string:key>/bids', methods=['GET', 'POST'])
def bids(key):
    pass
