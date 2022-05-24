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

from extensions import db
import models as m
from main import app, get_lnd_client, get_twitter
from main import get_token_from_request, get_user_from_token, user_required

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/healthcheck', methods=['GET'])
def healthcheck(): # TODO: I don't really like this, for some reason, but it is used in "dev" mode by docker-compose
    return jsonify({'success': True})

# TODO: It would be nice to extract this into a separate Python package that can be used by any (Flask?) project.
@api_blueprint.route('/api/login', methods=['GET'])
def login():
    """
    Log in with a Lightning wallet.
    """

    if 'k1' not in request.args:
        # first request to /login => we return a challenge (k1) and a QR code
        k1 = secrets.token_hex(32)

        db.session.add(m.LnAuth(k1=k1))
        db.session.commit()

        url = app.config['BASE_URL'] + f"/api/login?tag=login&k1={k1}"
        ln_url = lnurl.encode(url).bech32
        qr = BytesIO()
        pyqrcode.create(ln_url).svg(qr, omithw=True, scale=4)

        return jsonify({'k1': k1, 'lnurl': str(ln_url), 'qr': qr.getvalue().decode('utf-8')})

    lnauth = m.LnAuth.query.filter_by(k1=request.args['k1']).first()

    if not lnauth or lnauth.created_at < datetime.utcnow() - timedelta(minutes=m.LnAuth.EXPIRE_MINUTES):
        return jsonify({'message': "Verification failed."}), 400

    if 'key' in request.args and 'sig' in request.args:
        # request made by the Lightning wallet, includes a key and a signature

        if lnauth.key and request.args['key'] != lnauth.key:
            # lnauth should not have a "key" here, unless the user scanned the QR code already
            # but then the key in the request should match the key we saved on the previous scan
            app.logger.warning(f"Dubious request with a key {request.args['key']} different from the existing key for k1 {lnauth.k1}.")
            return jsonify({'message': "Verification failed."}), 400
        if not lnauth.key:
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

        return jsonify({})

    if not lnauth.key:
        # this is the browser continuously checking whether log in happened by passing in the challenge (k1)
        return jsonify({'success': False})

    # we are now logged in, so find the user, delete the lnauth and return the JWT token

    user = m.User.query.filter_by(key=lnauth.key).first()

    if not user:
        user = m.User(key=lnauth.key)
        db.session.add(user)

    db.session.delete(lnauth)
    db.session.commit()

    token = jwt.encode({'user_key': user.key, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token, 'user': user.to_dict()})

@api_blueprint.route('/api/users/me', methods=['GET', 'POST'])
@user_required
def me(user):
    if request.method == 'GET':
        return jsonify({'user': user.to_dict()})
    else:
        if 'nym' in request.json:
            return jsonify({'message': "Can't edit nym."}), 400 # yet, I guess...
        if 'twitter_username' in request.json:
            clean_username = request.json['twitter_username'] or ""
            if clean_username.startswith("@"):
                clean_username = clean_username[1:]
            if not clean_username:
                return jsonify({'message': "Invalid Twitter username!"}), 400
            if clean_username != user.twitter_username:
                user.twitter_username = clean_username
                twitter_user = get_twitter().get_user(user.twitter_username)
                if not twitter_user:
                    return jsonify({'message': "Twitter profile not found!"}), 400
                user.twitter_profile_image_url = twitter_user['profile_image_url']
                user.twitter_username_verified = False
        if 'contribution_percent' in request.json:
            user.contribution_percent = request.json['contribution_percent']
        try:
            db.session.commit()
        except IntegrityError:
            return jsonify({'message': "Somebody already registered this Twitter username!"}), 400
        return jsonify({'user': user.to_dict()})

@api_blueprint.route('/api/auctions', methods=['GET', 'POST'])
@user_required
def auctions(user):
    if request.method == 'GET':
        auctions = [a.to_dict(for_user=user.id) for a in user.auctions]
        return jsonify({'auctions': auctions})
    else:
        # TODO: prevent seller from creating too many auctions?

        for k in ['title', 'description', 'duration_hours', 'starting_bid', 'reserve_bid']:
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
        if auction.end_date and auction.end_date < datetime.utcnow():
            if auction.winning_bid_id is None and auction.contribution_payment_request is None:
                # auction ended, but no winning bid has been picked
                # => ask the user with the top bid to send the contribution
                top_bid = auction.get_top_bid()
                if top_bid:
                    auction.contribution_amount = int(auction.seller.contribution_percent / 100 * top_bid.amount)
                    if auction.contribution_amount < app.config['MINIMUM_CONTRIBUTION_AMOUNT']:
                        auction.contribution_amount = 0 # probably not worth the fees, at least in the next few years

                        # settle the contribution and pick the winner right away
                        auction.contribution_requested_at = auction.contribution_settled_at = datetime.utcnow()
                        auction.winning_bid_id = top_bid.id
                    else:
                        response = get_lnd_client().add_invoice(value=auction.contribution_amount)
                        auction.contribution_payment_request = response.payment_request
                        auction.contribution_requested_at = datetime.utcnow()
                    db.session.commit()
        return jsonify({'auction': auction.to_dict(for_user=(user.id if user else None))})
    else:
        if (not user) or (auction.seller_id != user.id):
            return jsonify({'message': "Unauthorized"}), 401

        if request.method == 'PUT':
            if auction.start_date and auction.start_date <= datetime.utcnow():
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
            # TODO: should we allow deletion of a started auction?
            db.session.delete(auction)
            db.session.commit()

            return jsonify({})

@api_blueprint.route('/api/auctions/<string:key>/start-twitter', methods=['PUT'])
@user_required
def start_twitter(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404
    if auction.seller_id != user.id:
        return jsonify({'message': "Unauthorized"}), 401
    twitter = get_twitter()
    twitter_user = twitter.get_user(user.twitter_username)
    if not twitter_user:
        return jsonify({'message': "Twitter profile not found!"}), 400
    user.twitter_profile_image_url = twitter_user['profile_image_url']
    tweet = twitter.get_auction_tweet(twitter_user['id'])
    if not tweet:
        return jsonify({'message': "Tweet not found."}), 400
    if tweet['auction_key'] != auction.key:
        return jsonify({'message': "Link in tweet is for another auction."}), 400
    if not tweet['photos']:
        return jsonify({'message': "Tweet does not have any attached pictures."}), 400

    user.twitter_username_verified = True
    auction.twitter_id = tweet['id']
    auction.start_date = datetime.utcnow()
    auction.end_date = auction.start_date + timedelta(hours=auction.duration_hours)
    for photo in tweet['photos']:
        media = m.Media(auction_id=auction.id, twitter_media_key=photo['media_key'], url=photo['url'])
        db.session.add(media)
    db.session.commit()

    return jsonify({})

@api_blueprint.route('/api/auctions/<string:key>/bids', methods=['POST'])
@user_required
def bids(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404

    if auction.start_date is None or auction.start_date > datetime.utcnow() or auction.end_date < datetime.utcnow():
        return jsonify({'message': "Auction not running."}), 403

    amount = int(request.json['amount'])

    top_bid = auction.get_top_bid()
    top_amount = top_bid.amount if top_bid else auction.starting_bid

    if amount <= top_amount:
        return jsonify({'message': f"Amount needs to be at least {top_amount}."}), 400

    response = get_lnd_client().add_invoice(value=app.config['LIGHTNING_INVOICE_AMOUNT'])

    payment_request = response.payment_request

    bid = m.Bid(auction=auction, buyer=user, amount=amount, payment_request=payment_request)
    db.session.add(bid)
    db.session.commit()

    qr = BytesIO()
    pyqrcode.create(payment_request).svg(qr, omithw=True, scale=4)

    return jsonify({'payment_request': payment_request, 'qr': qr.getvalue().decode('utf-8')})
