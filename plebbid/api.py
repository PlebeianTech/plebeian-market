from datetime import datetime, timedelta
from io import BytesIO
import os
import secrets

import dateutil.parser
import ecdsa
from ecdsa.keys import BadSignatureError
from flask import Blueprint, jsonify, request
import jwt
import lnurl
import pyqrcode
from sqlalchemy.exc import IntegrityError

from plebbid import models as m
from plebbid.main import app, db, token_required

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'success': True})

@api_blueprint.route('/sellers', methods=['POST'])
def add_seller():
    try:
        db.session.add(m.Seller(key=request.form['key']))
        db.session.commit()
        return jsonify({'success': True})
    except IntegrityError:
        return jsonify({'success': False, 'message': "Seller already registered."}), 400

@api_blueprint.route('/sellers/<string:key>/auctions', methods=['GET', 'POST'])
def auctions(key):
    seller = m.Seller.query.filter_by(key=key).first()
    if not seller:
        return jsonify({'success': False, 'message': "Not found."}), 404
    if request.method == 'GET':
        return jsonify({'success': True, 'auctions': [a.to_dict() for a in seller.auctions]})
    else:
        # TODO: prevent seller from creating too many auctions?

        for k in ['starts_at', 'ends_at', 'minimum_bid']:
            if k not in request.form:
                return jsonify({'success': False, 'message': f"Missing key: {k}."}), 400
        dates = {}
        for k in ['starts_at', 'ends_at']:
            try:
                dates[k] = dateutil.parser.isoparse(request.form[k])
            except ValueError:
                return jsonify({'success': False, 'message': f"Invalid date: {k}."}), 400
            if dates[k] < datetime.utcnow():
                return jsonify({'success': False, 'message': f"Date must be in the future: {k}."}), 400
        try:
            minimum_bid = int(request.form['minimum_bid'])
        except ValueError:
            return jsonify({'success': False, 'message': "Invalid minimum_bid."}), 400

        key = m.Auction.generate_key()
        max_short_id = db.session.query(db.func.max(m.Auction.short_id)).filter(m.Auction.seller == seller).scalar()
        new_short_id = max_short_id + 1 if max_short_id else 1
        auction = m.Auction(key=key, seller=seller, short_id=new_short_id,
            minimum_bid=minimum_bid, **dates)
        db.session.add(auction)
        db.session.commit()
        return jsonify({'success': True, 'key': key, 'short_id': new_short_id})

@api_blueprint.route('/sellers/<string:key>/auctions/<int:short_id>', methods=['GET', 'DELETE'])
def auction_by_short_id(key, short_id):
    seller = m.Seller.query.filter_by(key=key).first()
    if not seller:
        return jsonify({'success': False, 'message': "Not found."}), 404
    auction = m.Auction.query.filter_by(seller=seller, short_id=short_id).first()
    if not auction:
        return jsonify({'success': False, 'message': "Not found."}), 404
    if request.method == 'GET':
        return jsonify({'success': True, 'auction': auction.to_dict()})
    else:
        db.session.delete(auction)
        db.session.commit()
        return jsonify({'success': True})

@api_blueprint.route('/auctions/<string:key>', methods=['GET'])
def auction_by_key(key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'success': False, 'message': "Not found."}), 404
    return jsonify({'success': True, 'auction': auction.to_dict()})

@api_blueprint.route('/login', methods=['GET'])
def login():
    if 'k1' not in request.args:
        k1 = secrets.token_hex(32)
        url = app.config['BASE_URL'] + f"/login?tag=login&k1={k1}"
        qr = BytesIO()
        pyqrcode.create(lnurl.encode(url).bech32).svg(qr, scale=1)
        return jsonify({'qr': qr.getvalue().decode('utf-8')})

    for k in ['k1', 'key', 'sig']:
        if k not in request.args:
            return jsonify({'success': False, 'message': f"Missing key: {k}."}), 400
    try:
        app.logger.warn(request.args['k1'])
        app.logger.warn(request.args['key'])
        app.logger.warn(request.args['sig'])
        k1_bytes, key_bytes, sig_bytes = map(lambda k: bytes.fromhex(request.args[k]), ['k1', 'key', 'sig'])
    except ValueError:
        return jsonify({'success': False, 'message': f"Invalid parameter."}), 400

    vk = ecdsa.VerifyingKey.from_string(key_bytes, curve=ecdsa.SECP256k1)
    try:
        vk.verify_digest(sig_bytes, k1_bytes, sigdecode=ecdsa.util.sigdecode_der)
    except BadSignatureError:
        return jsonify({'success': False, 'message': "Verification failed."}), 400

    key = request.args['key']

    buyer = m.Buyer.query.filter_by(key=key).first()
    if not buyer:
        buyer = m.Buyer(key=key)
        db.session.add(buyer)
        db.session.commit()

    token = jwt.encode({'user_key': key, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token})

@api_blueprint.route('/auctions/<string:key>/bids', methods=['POST'])
@token_required
def bid(buyer, key):
    auction = m.Auction.query.filter_by(key=key).first_or_404()
    amount = request.form['amount']

    # TODO: validate amount!

    # TODO: generate a real invoice in LN!
    import random
    import string
    payment_request = ''.join(random.choice(string.ascii_lowercase) for i in range(12))

    bid = m.Bid(auction=auction, buyer=buyer, amount=amount, payment_request=payment_request)
    db.session.add(bid)
    db.session.commit()

    return jsonify({'success': True, 'payment_request': payment_request})
