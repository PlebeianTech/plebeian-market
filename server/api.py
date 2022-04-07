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

from server import models as m
from server.main import app, db, get_lnd_client
from server.main import get_token_from_request, get_user_from_token, user_required

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'success': True})

@api_blueprint.route('/api/auctions', methods=['GET', 'POST'])
@user_required
def auctions(user):
    if request.method == 'GET':
        auctions = [a.to_dict(for_user=user.id) for a in user.auctions]
        return jsonify({'success': True, 'auctions': auctions})
    else:
        # TODO: prevent seller from creating too many auctions?

        for k in ['starts_at', 'ends_at', 'minimum_bid']:
            if k not in request.form:
                return jsonify({'success': False, 'message': f"Missing key: {k}."}), 400
        dates = {}
        for k in ['starts_at', 'ends_at']:
            try:
                dates[k] = dateutil.parser.isoparse(request.form[k])
                if dates[k].tzinfo != dateutil.tz.tzutc():
                    return jsonify({'success': False, 'message': f"Date must be in UTC: {k}."}), 400
                dates[k] = dates[k].replace(tzinfo=None)
            except ValueError:
                return jsonify({'success': False, 'message': f"Invalid date: {k}."}), 400
            if dates[k] < datetime.utcnow():
                return jsonify({'success': False, 'message': f"Date must be in the future: {k}."}), 400
        try:
            minimum_bid = int(request.form['minimum_bid'])
        except ValueError:
            return jsonify({'success': False, 'message': "Invalid minimum_bid."}), 400

        auction = m.Auction(seller=user, minimum_bid=minimum_bid, **dates)
        db.session.add(auction)
        db.session.commit()
        return jsonify({'success': True, 'auction': auction.to_dict(for_user=user)})

@api_blueprint.route('/api/auctions/<string:key>', methods=['GET', 'DELETE'])
def auction(key):
    user = get_user_from_token(get_token_from_request())
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'success': False, 'message': "Not found."}), 404

    if request.method == 'GET':
        return jsonify({'success': True, 'auction': auction.to_dict(for_user=(user.id if user else None))})
    else:
        if (not user) or (auction.seller_id != user.id):
            return jsonify({'success': False, 'message': "Unauthorized"}), 401

        db.session.delete(auction)
        db.session.commit()

        return jsonify({'success': True})

@api_blueprint.route('/api/login', methods=['GET'])
def login():
    if 'k1' not in request.args:
        k1 = secrets.token_hex(32)

        db.session.add(m.LnAuth(k1=k1))
        db.session.commit()

        url = app.config['BASE_URL'] + f"/api/login?tag=login&k1={k1}"
        qr = BytesIO()
        pyqrcode.create(lnurl.encode(url).bech32).svg(qr, scale=4)

        return jsonify({'k1': k1, 'qr': qr.getvalue().decode('utf-8')})

    lnauth = m.LnAuth.query.filter_by(k1=request.args['k1']).first()

    if not lnauth: # TODO: check age of the lnauth as well!
        return jsonify({'success': False, 'message': "Invalid challenge."}), 400

    # TODO: check the key in request against the key in lnauth (if it is already there)?

    if 'key' in request.args and 'sig' in request.args and not lnauth.key:
        try:
            k1_bytes, key_bytes, sig_bytes = map(lambda k: bytes.fromhex(request.args[k]), ['k1', 'key', 'sig'])
        except ValueError:
            return jsonify({'success': False, 'message': "Invalid parameter."}), 400

        vk = ecdsa.VerifyingKey.from_string(key_bytes, curve=ecdsa.SECP256k1)
        try:
            vk.verify_digest(sig_bytes, k1_bytes, sigdecode=ecdsa.util.sigdecode_der)
        except BadSignatureError:
            return jsonify({'success': False, 'message': "Verification failed."}), 400

        lnauth.key = request.args['key']

        db.session.commit()

    if not lnauth.key:
        return jsonify({'success': False}), 200

    user = m.User.query.filter_by(key=lnauth.key).first()

    # TODO: delete lnauth here or on first successful request with this user?
    if not user:
        user = m.User(key=lnauth.key)
        db.session.add(user)
        db.session.commit()

    token = jwt.encode({'user_key': user.key, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token})

@api_blueprint.route('/api/auctions/<string:key>/bids', methods=['POST'])
@user_required
def bid(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'success': False, 'message': "Not found."}), 404

    amount = int(request.form['amount'])

    # TODO: validate amount!

    response = get_lnd_client().add_invoice(value=amount)

    payment_request = response.payment_request

    bid = m.Bid(auction=auction, buyer=user, amount=amount, payment_request=payment_request)
    db.session.add(bid)
    db.session.commit()

    qr = BytesIO()
    pyqrcode.create(payment_request).svg(qr, scale=4)

    return jsonify({'success': True, 'payment_request': payment_request, 'qr': qr.getvalue().decode('utf-8')})
