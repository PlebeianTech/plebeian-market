from datetime import datetime, timedelta
from io import BytesIO
import os
import secrets

import dateutil.parser
import ecdsa
from ecdsa.keys import BadSignatureError
from flask import Blueprint, jsonify, request, Response
import jwt
import lnurl
import pyqrcode
import rjsmin
from sqlalchemy.exc import IntegrityError

from plebbid import models as m
from plebbid.main import app, db, get_lnd_client
from plebbid.main import buyer_required, get_buyer_from_token, get_token_from_request

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'success': True})

SCRIPTS = None
@api_blueprint.route('/scripts', methods=['GET'])
def scripts():
    global SCRIPTS
    if not SCRIPTS:
        scripts = f"var BASE_URL = '{app.config['BASE_URL']}';\n"
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'js')
        for filename in ['utils.js', 'auction.js']:
            with open(os.path.join(path, filename)) as f:
                scripts += f.read() + "\n"
        SCRIPTS = rjsmin.jsmin(scripts)
    return Response(SCRIPTS, mimetype="application/javascript")

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
        auctions = [a.to_dict(for_seller=seller.id) for a in seller.auctions]
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
        return jsonify({'success': True, 'auction': auction.to_dict(for_seller=seller.id)})
    else:
        db.session.delete(auction)
        db.session.commit()
        return jsonify({'success': True})

@api_blueprint.route('/auctions/<string:key>', methods=['GET'])
def auction_by_key(key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'success': False, 'message': "Not found."}), 404

    buyer = get_buyer_from_token(get_token_from_request())

    return jsonify({'success': True, 'auction': auction.to_dict(for_buyer=(buyer.id if buyer else None))})

@api_blueprint.route('/login', methods=['GET'])
def login():
    if 'k1' not in request.args:
        k1 = secrets.token_hex(32)

        db.session.add(m.LnAuth(k1=k1))
        db.session.commit()

        url = app.config['BASE_URL'] + f"/login?tag=login&k1={k1}"
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

    buyer = m.Buyer.query.filter_by(key=lnauth.key).first()

    # TODO: delete lnauth here or on first successful request with this user?
    if not buyer:
        buyer = m.Buyer(key=lnauth.key)
        db.session.add(buyer)
        db.session.commit()

    token = jwt.encode({'user_key': buyer.key, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token})

@api_blueprint.route('/auctions/<string:key>/bids', methods=['POST'])
@buyer_required
def bid(buyer, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'success': False, 'message': "Not found."}), 404

    amount = int(request.form['amount'])

    # TODO: validate amount!

    response = get_lnd_client().add_invoice(value=amount)

    payment_request = response.payment_request

    bid = m.Bid(auction=auction, buyer=buyer, amount=amount, payment_request=payment_request)
    db.session.add(bid)
    db.session.commit()

    qr = BytesIO()
    pyqrcode.create(payment_request).svg(qr, scale=4)

    return jsonify({'success': True, 'payment_request': payment_request, 'qr': qr.getvalue().decode('utf-8')})
