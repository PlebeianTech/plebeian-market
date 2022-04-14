from datetime import datetime, timedelta
from io import BytesIO
import os
import secrets

import ecdsa
from ecdsa.keys import BadSignatureError
from flask import Blueprint, jsonify, request
import jwt
import lnurl
import pyqrcode
from sqlalchemy.exc import IntegrityError

from server import models as m
from server.main import app, db, get_lnd_client
from server.main import get_token_from_request, get_user_from_token, user_required

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'success': True})

@api_blueprint.route('/api/login', methods=['GET'])
def login():
    if 'k1' not in request.args:
        k1 = secrets.token_hex(32)

        db.session.add(m.LnAuth(k1=k1))
        db.session.commit()

        url = app.config['BASE_URL'] + f"/api/login?tag=login&k1={k1}"
        qr = BytesIO()
        pyqrcode.create(lnurl.encode(url).bech32).svg(qr, omithw=True, scale=4)

        return jsonify({'k1': k1, 'qr': qr.getvalue().decode('utf-8')})

    lnauth = m.LnAuth.query.filter_by(k1=request.args['k1']).first()

    if not lnauth: # TODO: check age of the lnauth as well!
        return jsonify({'message': "Invalid challenge."}), 400

    # TODO: check the key in request against the key in lnauth (if it is already there)?

    if 'key' in request.args and 'sig' in request.args and not lnauth.key:
        try:
            k1_bytes, key_bytes, sig_bytes = map(lambda k: bytes.fromhex(request.args[k]), ['k1', 'key', 'sig'])
        except ValueError:
            return jsonify({'message': "Invalid parameter."}), 400

        vk = ecdsa.VerifyingKey.from_string(key_bytes, curve=ecdsa.SECP256k1)
        try:
            vk.verify_digest(sig_bytes, k1_bytes, sigdecode=ecdsa.util.sigdecode_der)
        except BadSignatureError:
            return jsonify({'message': "Verification failed."}), 400

        lnauth.key = request.args['key']

        db.session.commit()

    if not lnauth.key:
        return jsonify({'success': False})

    user = m.User.query.filter_by(key=lnauth.key).first()

    # TODO: delete lnauth here or on first successful request with this user?
    if not user:
        user = m.User(key=lnauth.key)
        db.session.add(user)
        db.session.commit()

    token = jwt.encode({'user_key': user.key, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token})

@api_blueprint.route('/api/auctions', methods=['GET', 'POST'])
@user_required
def auctions(user):
    if request.method == 'GET':
        auctions = [a.to_dict(for_user=user.id) for a in user.auctions]
        return jsonify({'auctions': auctions})
    else:
        # TODO: prevent seller from creating too many auctions?

        for k in ['starts_at', 'ends_at', 'minimum_bid']:
            if k not in request.json:
                return jsonify({'message': f"Missing key: {k}."}), 400

        try:
            validated = m.Auction.validate_dict(request.json)
        except m.ValidationError as e:
            return jsonify({'message': e.message}), 400

        auction = m.Auction(seller=user, **validated)
        db.session.add(auction)
        db.session.commit()

        return jsonify({'auction': auction.to_dict(for_user=user)})

@api_blueprint.route('/api/auctions/<string:key>', methods=['GET', 'PUT', 'DELETE'])
def auction(key):
    user = get_user_from_token(get_token_from_request())
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404

    if request.method == 'GET':
        return jsonify({'auction': auction.to_dict(for_user=(user.id if user else None))})
    else:
        if (not user) or (auction.seller_id != user.id):
            return jsonify({'message': "Unauthorized"}), 401

        if request.method == 'PUT':
            if auction.starts_at <= datetime.utcnow():
                return jsonify({'message': "Cannot edit an auction once started."}), 403
            try:
                validated = m.Auction.validate_dict(request.json)
            except m.ValidationError as e:
                return jsonify({'message': e.message}), 400

            for k, v in validated.items():
                setattr(auction, k, v)
            db.session.commit()

            return jsonify({})
        elif request.method == 'DELETE':
            db.session.delete(auction)
            db.session.commit()

            return jsonify({})

@api_blueprint.route('/api/auctions/<string:key>/bids', methods=['POST'])
@user_required
def bid(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404

    if auction.starts_at > datetime.utcnow() or auction.ends_at < datetime.utcnow():
        return jsonify({'message': "Auction not running."}), 403

    amount = int(request.json['amount'])

    try:
        max_amount = max(bid.amount for bid in auction.bids if bid.settled_at)
    except ValueError:
        max_amount = auction.minimum_bid

    if amount <= max_amount:
        return jsonify({'message': f"Amount needs to be at least {max_amount}."}), 400

    # TODO: extend auction if bidding in the last few minutes?

    response = get_lnd_client().add_invoice(value=app.config['LIGHTNING_INVOICE_AMOUNT'])

    payment_request = response.payment_request

    bid = m.Bid(auction=auction, buyer=user, amount=amount, payment_request=payment_request)
    db.session.add(bid)
    db.session.commit()

    qr = BytesIO()
    pyqrcode.create(payment_request).svg(qr, omithw=True, scale=4)

    return jsonify({'payment_request': payment_request, 'qr': qr.getvalue().decode('utf-8')})
