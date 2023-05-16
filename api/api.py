import bleach
import btc2fiat
from datetime import datetime, timedelta
import ecdsa
from ecdsa.keys import BadSignatureError
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, jsonify, redirect, request
from io import BytesIO
import json
import jwt
import lnurl
from nostr.key import PrivateKey
import os
import pyqrcode
import secrets
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
import time

from extensions import db
import models as m
from main import app, get_lnd_client, get_nostr_client, get_s3, get_twitter
from main import get_token_from_request, get_user_from_token, user_required
from main import MempoolSpaceError
from utils import usd2sats, parse_xpub, UnknownKeyTypeError

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/healthcheck', methods=['GET'])
def healthcheck(): # TODO: I don't really like this, for some reason, but it is used in "dev" mode by docker-compose
    return jsonify({'success': True})

# PUT would make more sense than GET, but the lightning wallets only do GET - perhaps we could split this in two parts - the part called by our app and the GET done by the wallet
@api_blueprint.route('/api/login', methods=['GET'], defaults={'deprecated': True, 'create_user': True}) # deprecated, but still used by the WP plugin
@api_blueprint.route('/api/login/lnurl', methods=['GET'], defaults={'deprecated': False, 'create_user': False})
@api_blueprint.route('/api/signup/lnurl', methods=['GET'], defaults={'deprecated': False, 'create_user': True})
def auth_lnurl(deprecated, create_user):
    if deprecated:
        return redirect(f"{app.config['API_BASE_URL']}/api/login/lnurl", code=301)

    if 'k1' not in request.args:
        # first request to /login => we return a challenge (k1) and a QR code
        k1 = secrets.token_hex(32)

        db.session.add(m.LnAuth(k1=k1))
        db.session.commit()

        url = app.config['API_BASE_URL'] + f"/api/login/lnurl?tag=login&k1={k1}"
        ln_url = lnurl.encode(url).bech32
        qr = BytesIO()
        pyqrcode.create(ln_url).svg(qr, omithw=True, scale=4)

        return jsonify({'k1': k1, 'lnurl': str(ln_url), 'qr': qr.getvalue().decode('utf-8')})

    lnauth = m.LnAuth.query.filter_by(k1=request.args['k1']).first()

    if not lnauth:
        return jsonify({'message': "Verification failed."}), 400

    if lnauth.created_at < datetime.utcnow() - timedelta(minutes=app.config['LNAUTH_EXPIRE_MINUTES']):
        return jsonify({'message': "Login token expired."}), 410

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

    user = m.User.query.filter_by(lnauth_key=lnauth.key).first()

    if not user:
        if create_user:
            user = m.User(lnauth_key=lnauth.key)
            db.session.add(user)
        else:
            return jsonify({'message': "User not found. Please create an account first."}), 400
    else:
        if create_user:
            return jsonify({'message': "User with this key already exists. Please log in."}), 409

    db.session.delete(lnauth)
    db.session.commit()

    token_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=app.config['JWT_EXPIRE_DAYS']),
        'r': secrets.token_hex(4), # just 4 random bytes, to ensure the tokens are unique (mostly for tests)
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token, 'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/login/nostr', methods=['PUT'], defaults={'create_user': False})
@api_blueprint.route('/api/signup/nostr', methods=['PUT'], defaults={'create_user': True})
def auth_nostr(create_user):
    if 'key' not in request.json:
        return jsonify({'message': "Missing key."}), 400

    auth = m.NostrAuth.query.filter_by(key=request.json['key']).first()

    nostr = get_nostr_client(None)

    if request.json.get('send_verification_phrase'):
        if auth:
            if app.config['ENV'] != 'test':
                if auth.verification_phrase_sent_at and auth.verification_phrase_sent_at >= datetime.utcnow() - timedelta(minutes=1):
                    return jsonify({'message': "Please wait at least one minuted before requesting a new verification phrase!"}), 400
        else:
            auth = m.NostrAuth(key=request.json['key'])
            db.session.add(auth)

        auth.generate_verification_phrase()
        if not nostr.send_dm(recipient_public_key=auth.key, body=auth.verification_phrase):
            return jsonify({'message': "Error sending Nostr DM."}), 500
        auth.verification_phrase_sent_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'sent': True})

    if 'verification_phrase' not in request.json:
        return jsonify({'message': "Missing verification phrase."}), 400

    if not auth:
        # this is a strange case - they provide a verification phrase, but there is no log in attempt for the given key - no need to give too much info
        return jsonify({'message': "Verification failed."}), 400

    if auth.verification_phrase_check_counter > 5:
        return jsonify({'message': "Please try requesting a new verification phrase!"}), 400

    clean_phrase = ' '.join([w for w in request.json['verification_phrase'].lower().split(' ') if w])

    if nostr.get_auth_verification_phrase(auth) == clean_phrase:
        user = m.User.query.filter_by(nostr_public_key=auth.key, nostr_public_key_verified=True).first()

        if not user:
            if create_user:
                user = m.User(nostr_public_key=auth.key, nostr_public_key_verified=True)
                db.session.add(user)
            else:
                return jsonify({'message': "User not found. Please create an account first."}), 400
        else:
            if create_user:
                return jsonify({'message': "User with this key already exists. Please log in."}), 409

        if not user:
            user = m.User(nostr_public_key=auth.key, nostr_public_key_verified=True)
            db.session.add(user)

        db.session.delete(auth)

        db.session.commit()

        token_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=app.config['JWT_EXPIRE_DAYS']),
            'r': secrets.token_hex(4), # just 4 random bytes, to ensure the tokens are unique (mostly for tests)
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], "HS256")

        return jsonify({'success': True, 'token': token, 'user': user.to_dict(for_user=user.id)})
    else:
        time.sleep(2 ** auth.verification_phrase_check_counter)
        auth.verification_phrase_check_counter += 1
        db.session.commit()
        return jsonify({'message': "Wrong incantation..."}), 400

@api_blueprint.route('/api/users/<nym>', methods=['GET'])
def get_profile(nym):
    requesting_user = get_user_from_token(get_token_from_request())
    for_user_id = requesting_user.id if requesting_user else None
    user = m.User.query.filter_by(nym=nym).first()
    if not user:
        return jsonify({'message': "User not found."}), 404
    return jsonify({'user': user.to_dict(for_user=for_user_id)})

@api_blueprint.route('/api/users/me', methods=['GET'])
@user_required
def get_me(user):
    return jsonify({'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/users/me', methods=['PUT'])
@user_required
def put_me(user):
    if 'nym' in request.json:
        clean_nym = (request.json['nym'] or "").lower().strip()
        if clean_nym != user.nym:
            if len(clean_nym) < 3:
                return jsonify({'message': "Your nym needs to be at least 3 characters long!"}), 400
            if not clean_nym.isalnum():
                return jsonify({'message': "Your nym can only contain letters and numbers!"}), 400
            if m.User.query.filter_by(nym=clean_nym).one_or_none():
                return jsonify({'message': "Your nym is already in use!", 'field': 'nym', 'reason': 'duplicated'}), 400
            user.nym = clean_nym

    if 'profile_image_url' in request.json:
        user.fetch_external_profile_image(request.json['profile_image_url'], get_s3())

    if 'email' in request.json:
        clean_email = (request.json['email'] or "").lower().strip()
        try:
            clean_email = validate_email(clean_email).email
        except EmailNotValidError:
            return jsonify({'message': "Your email address is not valid."}), 400
        if clean_email != user.email:
            if m.User.query.filter_by(email=clean_email).one_or_none():
                return jsonify({'message': "Somebody already registered this email address!"}), 400
            user.email = clean_email
            user.email_verified = False

    if 'telegram_username' in request.json:
        clean_username = (request.json['telegram_username'] or "").lower().strip()
        if clean_username.startswith("@"):
            clean_username = clean_username.removeprefix("@")
        if clean_username != user.telegram_username:
            if len(clean_username) < 3:
                return jsonify({'message': "Your Telegram username needs to be at least 3 characters long!"}), 400
            if not clean_username.replace("_", "").isalnum():
                return jsonify({'message': "Your Telegram username can only contain letters, numbers and underscores!"}), 400
            if m.User.query.filter_by(telegram_username=clean_username).one_or_none():
                return jsonify({'message': "Somebody already registered this Telegram username!"}), 400
            user.telegram_username = clean_username
            user.telegram_username_verified = False

    if 'twitter_username' in request.json:
        clean_username = (request.json['twitter_username'] or "").lower().strip()
        if clean_username.startswith("@"):
            clean_username = clean_username.removeprefix("@")
        if clean_username != user.twitter_username:
            if len(clean_username) < 3:
                return jsonify({'message': "Your Twitter username needs to be at least 3 characters long!"}), 400
            if not clean_username.replace("_", "").isalnum():
                return jsonify({'message': "Your Twitter username can only contain letters, numbers and underscores!"}), 400
            if m.User.query.filter_by(twitter_username=clean_username).one_or_none():
                return jsonify({'message': "Somebody already registered this Twitter username!"}), 400
            if user.nym == user.twitter_username:
                # NB: if the user has set a custom nym, don't overwrite that!
                user.nym = clean_username

            user.twitter_username = clean_username
            user.twitter_username_verified = False
            user.generate_verification_phrase('twitter')

            twitter = get_twitter()
            twitter_user = twitter.get_user(user.twitter_username)
            if not twitter_user:
                return jsonify({'message': "Twitter profile not found!"}), 400

            if app.config['ENV'] == 'prod':
                if user.twitter_username not in app.config['TWITTER_USER_MIN_AGE_DAYS_WHITELIST']:
                    if twitter_user['created_at'] > (datetime.utcnow() - timedelta(days=app.config['TWITTER_USER_MIN_AGE_DAYS'])):
                        return jsonify({'message': f"Twitter profile needs to be at least {app.config['TWITTER_USER_MIN_AGE_DAYS']} days old!"}), 400

            if not user.fetch_external_profile_image(twitter_user['profile_image_url'], get_s3()):
                return jsonify({'message': "Error fetching profile picture!"}), 400

            if not user.fetch_twitter_profile_banner(twitter_user['profile_banner_url'], get_s3()):
                return jsonify({'message': "Error fetching profile banner!"}), 400

            if not twitter.send_dm(twitter_user['id'], user.twitter_verification_phrase):
                return jsonify({'message': "Error sending Twitter DM!"}), 500
            user.twitter_verification_phrase_sent_at = datetime.utcnow()

    if 'nostr_public_key' in request.json:
        user.nostr_public_key = request.json['nostr_public_key']
        user.nostr_public_key_verified = False
        user.generate_verification_phrase('nostr')

        if not get_nostr_client(None).send_dm(recipient_public_key=user.nostr_public_key, body=user.nostr_verification_phrase):
            return jsonify({'message': "Error sending Nostr DM!"}), 500
        user.nostr_verification_phrase_sent_at = datetime.utcnow()

    if 'contribution_percent' in request.json:
        user.contribution_percent = request.json['contribution_percent']

    if 'wallet' in request.json:
        try:
            k = parse_xpub(request.json['wallet'])
        except UnknownKeyTypeError as e:
            return jsonify({'message': "Invalid wallet."}), 400
        try:
            first_address = k.subkey(0).subkey(0).address()
        except AttributeError:
            return jsonify({'message': "Invalid wallet."}), 400
        user.wallet = request.json['wallet']
        user.wallet_index = 0

    if 'stall_name' in request.json or 'stall_description' in request.json or 'shipping_from' in request.json or 'shipping_domestic_usd' in request.json or 'shipping_worldwide_usd' in request.json:
        if 'stall_name' in request.json:
            user.stall_name = bleach.clean(request.json['stall_name'])
        if 'stall_description' in request.json:
            user.stall_description = bleach.clean(request.json['stall_description'])
        if 'shipping_from' in request.json:
            user.shipping_from = bleach.clean(request.json['shipping_from'])
        if 'shipping_domestic_usd' in request.json:
            try:
                user.shipping_domestic_usd = float(request.json['shipping_domestic_usd'])
            except (ValueError, TypeError):
                user.shipping_domestic_usd = 0
        if 'shipping_worldwide_usd' in request.json:
            try:
                user.shipping_worldwide_usd = float(request.json['shipping_worldwide_usd'])
            except (ValueError, TypeError):
                user.shipping_worldwide_usd = 0
        user.ensure_stall_key()
        get_nostr_client(user).publish_stall(user.identity, user.stall_name, user.stall_description, 'USD', user.shipping_from, user.shipping_domestic_usd, user.shipping_worldwide_usd)

    if 'nostr_private_key' in request.json:
        user.nostr_private_key = request.json['nostr_private_key']

    try:
        db.session.commit()
    except IntegrityError:
        app.logger.exception(f"Error while saving user profile. {user.id=}")

        # there are very few cases where this could happen
        # namely with some old users that were created before we started saving the "clean" version of nym / twitter in the DB
        return jsonify({'message': "Please retry or contact support!"}), 500

    return jsonify({'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/users/me/verify/twitter', methods=['PUT'])
@user_required
def verify_twitter(user):
    if request.json.get('resend'):
        if user.twitter_verification_phrase_sent_at and user.twitter_verification_phrase_sent_at >= datetime.utcnow() - timedelta(minutes=1):
            return jsonify({'message': "Please wait at least one minuted before requesting a new verification phrase!"}), 400
        user.generate_verification_phrase('twitter')
        twitter = get_twitter()
        twitter_user = twitter.get_user(user.twitter_username)
        if not twitter_user:
            return jsonify({'message': "Twitter user not found!"}), 500
        if not twitter.send_dm(twitter_user['id'], user.twitter_verification_phrase):
            return jsonify({'message': f"Please allow DMs from @{app.config['TWITTER_USER']}"}), 400
        user.twitter_verification_phrase_sent_at = datetime.utcnow()
        db.session.commit()
        return jsonify({})

    if not request.json.get('phrase'):
        return jsonify({'message': "Please provide the verification phrase!"}), 400

    if user.twitter_verification_phrase_check_counter > 5:
        return jsonify({'message': "Please try requesting a new verification phrase!"}), 400

    clean_phrase = ' '.join([w for w in request.json['phrase'].lower().split(' ') if w])

    if get_twitter().get_verification_phrase(user) == clean_phrase:
        user.twitter_username_verified = True
        db.session.commit()
        return jsonify({})
    else:
        time.sleep(2 ** user.twitter_verification_phrase_check_counter)
        user.twitter_verification_phrase_check_counter += 1
        db.session.commit()
        return jsonify({'message': "Invalid verification phrase."}), 400

@api_blueprint.route('/api/users/me/verify/nostr', methods=['PUT'])
@user_required
def verify_nostr(user):
    if request.json.get('resend'):
        if user.nostr_verification_phrase_sent_at and user.nostr_verification_phrase_sent_at >= datetime.utcnow() - timedelta(minutes=1):
            return jsonify({'message': "Please wait at least one minuted before requesting a new verification phrase!"}), 400
        user.generate_verification_phrase('nostr')
        if not get_nostr_client(None).send_dm(recipient_public_key=user.nostr_public_key, body=user.nostr_verification_phrase):
            return jsonify({'message': "Error sending Nostr DM!"}), 500
        user.nostr_verification_phrase_sent_at = datetime.utcnow()
        db.session.commit()
        return jsonify({})

    if not request.json.get('phrase'):
        return jsonify({'message': "Please provide the verification phrase!"}), 400

    if user.nostr_verification_phrase_check_counter > 5:
        return jsonify({'message': "Please try requesting a new verification phrase!"}), 400

    clean_phrase = ' '.join([w for w in request.json['phrase'].lower().split(' ') if w])

    if get_nostr_client(None).get_verification_phrase(user) == clean_phrase:
        user.nostr_public_key_verified = True
        db.session.commit()
        return jsonify({})
    else:
        time.sleep(2 ** user.nostr_verification_phrase_check_counter)
        user.nostr_verification_phrase_check_counter += 1
        db.session.commit()
        return jsonify({'message': "Invalid verification phrase."}), 400

# request made by the browser; note that it requires a logged in user!
@api_blueprint.route("/api/users/me/verify/lnurl", methods=['PUT'])
@user_required
def verify_lnurl_put(user):
    if 'k1' not in request.json:
        # first request => we return a challenge (k1) and a QR code
        user.new_lnauth_key = None
        user.new_lnauth_key_k1 = secrets.token_hex(32)
        user.new_lnauth_key_k1_generated_at = datetime.utcnow()
        db.session.commit()

        url = app.config['API_BASE_URL'] + f"/api/users/me/verify/lnurl?tag=login&k1={user.new_lnauth_key_k1}"
        ln_url = lnurl.encode(url).bech32
        qr = BytesIO()
        pyqrcode.create(ln_url).svg(qr, omithw=True, scale=4)

        return jsonify({'k1': user.new_lnauth_key_k1, 'lnurl': str(ln_url), 'qr': qr.getvalue().decode('utf-8')})

    if request.json['k1'] != user.new_lnauth_key_k1:
        return jsonify({'message': "Verification failed."}), 400

    if user.new_lnauth_key_k1_generated_at < datetime.utcnow() - timedelta(minutes=app.config['LNAUTH_EXPIRE_MINUTES']):
        return jsonify({'message': "Auth token expired."}), 410

    if user.new_lnauth_key is not None:
        if user.new_lnauth_key == user.lnauth_key:
            # new key was verified AND it can be used for logging in now
            return jsonify({'success': True})
        else:
            # the new key was verified, but we didn't manage to set it as the "main" key,
            # which means it was a duplicate!
            # ... see the logic in verify_lnurl_get (GET /api/users/me/verify/lnurl) to understand why!
            return jsonify({'message': "This wallet is already associated with another Plebeian Market user!"}), 400
    else:
        # waiting for the user to scan the QR code...
        return jsonify({'success': False})

# request made by the Lightning wallet, includes a key and a signature
@api_blueprint.route("/api/users/me/verify/lnurl", methods=['GET'])
def verify_lnurl_get():
    if 'key' in request.args and 'sig' in request.args:
        user = m.User.query.filter_by(new_lnauth_key_k1=request.args['k1']).first()

        if not user:
            return jsonify({'message': "Verification failed."}), 400

        if user.new_lnauth_key and request.args['key'] != user.new_lnauth_key:
            # the user should not have a "lnauth_key" here, unless the user scanned the QR code already
            # but then the key in the request should match the key we saved on the previous scan
            app.logger.warning(f"Dubious request with a key {request.args['key']} different from the existing key for k1 {user.new_lnauth_key_k1}.")
            return jsonify({'message': "Verification failed."}), 400
        if not user.new_lnauth_key:
            try:
                k1_bytes, key_bytes, sig_bytes = map(lambda k: bytes.fromhex(request.args[k]), ['k1', 'key', 'sig'])
            except ValueError:
                return jsonify({'message': "Invalid parameter."}), 400

            vk = ecdsa.VerifyingKey.from_string(key_bytes, curve=ecdsa.SECP256k1)
            try:
                vk.verify_digest(sig_bytes, k1_bytes, sigdecode=ecdsa.util.sigdecode_der)
            except BadSignatureError:
                return jsonify({'message': "Verification failed."}), 400

            # at this point, the new key is verified, so let's save it!

            # first, save it under new_lnauth_key, which allows dupes, so it won't fail
            user.new_lnauth_key = request.args['key']

            db.session.commit()

            # now try to save it under the "main" key, which may fail in case of dupes!
            user.lnauth_key = request.args['key']

            # NB: the reason why we do this "two stage commit" is because we want to show an error message
            # in the request made by the browser - see verify_lnurl_put (PUT /api/users/me/verify/lnurl)
            # for an error that occured in this request (which is made by the mobile wallet)
            # simply returning an error here would leave the user looking at the browser confused

            try:
                db.session.commit()
            except IntegrityError:
                app.logger.warning(f"Attempt to link existing LN key for user {user.id=}.")
                return jsonify({'message': "User with this key already exists!"}), 400

        return jsonify({})

@api_blueprint.route("/api/users/me/relays", methods=['GET', 'POST'])
@user_required
def user_relays(user):
    if request.method == 'GET':
        return jsonify({'relays': [{'id': ur.relay_id, 'url': ur.relay.url} for ur in m.UserRelay.query.filter_by(user_id=user.id)]})
    elif request.method == 'POST':
        relay = m.Relay.query.filter_by(url=request.json['url']).one_or_none()
        if not relay:
            relay = m.Relay(url=request.json['url'])
            db.session.add(relay)
            db.session.commit()
        db.session.add(m.UserRelay(user_id=user.id, relay_id=relay.id))
        db.session.commit()
        return jsonify({'relay': {'id': relay.id, 'url': relay.url}})

@api_blueprint.route("/api/users/me/relays/<int:relay_id>", methods=['DELETE'])
@user_required
def delete_user_relay(user, relay_id):
    ur = m.UserRelay.query.filter_by(user_id=user.id, relay_id=relay_id).one_or_none()
    if not ur:
        return jsonify({'message': "Not found."}), 404
    db.session.delete(ur)
    db.session.commit()
    return jsonify({})

@api_blueprint.route('/api/users/me/notifications', methods=['GET', 'PUT'])
@user_required
def user_notifications(user):
    existing_notifications = {
        n.notification_type: n for n in m.UserNotification.query.filter_by(user_id=user.id).all()
    }
    if request.method == 'GET':
        notifications = []
        for t in m.NOTIFICATION_TYPES:
            if t in existing_notifications:
                notifications.append((False, existing_notifications[t]))
            else:
                notifications.append((True, m.UserNotification(notification_type=t, action=m.NOTIFICATION_TYPES[t].default_action)))
        return jsonify({'notifications': [n.to_dict() | {'is_default': is_default} for (is_default, n) in notifications]})
    elif request.method == 'PUT':
        for notification in request.json['notifications']:
            if notification['notification_type'] not in existing_notifications:
                db.session.add(m.UserNotification(
                    user_id=user.id,
                    notification_type=notification['notification_type'],
                    action=notification['action']))
            else:
                existing_notifications[notification['notification_type']].action = notification['action']
        db.session.commit()
        return jsonify({})

@api_blueprint.route('/api/users/me/messages', methods=['GET'])
@user_required
def get_messages(user):
    # by default we only return INTERNAL messages (to be shown in the UI),
    # but using the "via" parameter, we can request additional messages,
    # for example via=TWITTER_DM will return all messages sent to this user via TWITTER_DM
    via = request.args.get('via') or 'INTERNAL'

    if via == 'all':
        messages = user.messages
    else:
        messages = m.Message.query.filter_by(user_id=user.id, notified_via=via).all()

    return jsonify({'messages': [m.to_dict() for m in messages]})

@api_blueprint.route('/api/users/me/sales', methods=['GET'])
@user_required
def get_sales(user):
    sales = m.Sale.query.filter(m.Item.id == m.Sale.item_id, m.Item.seller_id == user.id).order_by(desc(m.Sale.requested_at)).all()

    return jsonify({'sales': [s.to_dict() for s in sales]})

@api_blueprint.route('/api/users/me/purchases', methods=['GET'])
@user_required
def get_purchases(user):
    purchases = m.Sale.query.filter(m.Sale.buyer_id == user.id).order_by(desc(m.Sale.requested_at)).all()

    return jsonify({'purchases': [p.to_dict() for p in purchases]})

@api_blueprint.route("/api/users/me/auctions",
    defaults={'cls': m.Auction, 'singular': 'auction', 'has_item': True, 'campaign_key': None},
    methods=['POST'])
@api_blueprint.route("/api/users/me/listings",
    defaults={'cls': m.Listing, 'singular': 'listing', 'has_item': True, 'campaign_key': None},
    methods=['POST'])
@api_blueprint.route("/api/users/me/campaigns",
    defaults={'cls': m.Campaign, 'singular': 'campaign', 'has_item': False, 'campaign_key': None},
    methods=['POST'])
@api_blueprint.route("/api/campaigns/<campaign_key>/auctions",
    defaults={'cls': m.Auction, 'singular': 'auction', 'has_item': True},
    methods=['POST'])
@api_blueprint.route("/api/campaigns/<campaign_key>/listings",
    defaults={'cls': m.Listing, 'singular': 'listing', 'has_item': True},
    methods=['POST'])
@user_required
def post_entity(user, cls, singular, has_item, campaign_key):
    campaign = None
    if campaign_key:
        campaign = m.Campaign.query.filter_by(key=campaign_key).first()
        if not campaign:
            return jsonify({'message': "Not found."}), 404

    for k in cls.REQUIRED_FIELDS:
        if k not in request.json:
            return jsonify({'message': f"Missing key: {k}."}), 400

    try:
        validated_item = m.Item.validate_dict(request.json, for_method='POST') if has_item else {}
        validated_entity = cls.validate_dict(request.json, for_method='POST')
    except m.ValidationError as e:
        return jsonify({'message': e.message}), 400

    item = None
    if has_item:
        item = m.Item(seller=user, **validated_item)
        db.session.add(item)
        db.session.commit()

    entity = cls(**validated_entity)
    entity.generate_key()
    if campaign:
        entity.campaign = campaign
    if item:
        entity.item = item
    if isinstance(entity, m.Campaign):
        entity.owner = user
    db.session.add(entity)
    db.session.commit()

    if isinstance(entity, m.Auction):
        # follow your own auctions!
        user_auction = m.UserAuction(user_id=user.id, auction_id=entity.id, following=True)
        db.session.add(user_auction)
        db.session.commit()

    return jsonify({'key': entity.key, singular: entity.to_dict(for_user=user.id)})

@api_blueprint.route('/api/auctions/active',
    defaults={'cls': m.Auction, 'plural': 'auctions', 'featured': False},
    methods=['GET'])
@api_blueprint.route('/api/listings/active',
    defaults={'cls': m.Listing, 'plural': 'listings', 'featured': False},
    methods=['GET'])
@api_blueprint.route('/api/campaigns/active',
    defaults={'cls': m.Campaign, 'plural': 'campaigns', 'featured': False},
    methods=['GET'])
@api_blueprint.route('/api/auctions/featured',
    defaults={'cls': m.Auction, 'plural': 'auctions', 'featured': True},
    methods=['GET'])
@api_blueprint.route('/api/listings/featured',
    defaults={'cls': m.Listing, 'plural': 'listings', 'featured': True},
    methods=['GET'])
def get_entities(cls, plural, featured):
    """
    Active auctions are all auctions currently running.
    Active listings are all listings that have been published and are still available for sale.
    Active campaigns are currently all campaigns. We don't have a way to mark a campaign as "ended", but that should eventually be added.
    Featured auctions/listings are subsets of the active auctions/listings:
        currently they simply exclude items that the moderators have marked as hidden,
        but we will eventually have a better algorithm to pick "featured" items.
    There are no "featured campaigns" because users can't (yet) add their own campaigns, so we only have our own.
        Also, since Campaign is not related to Items, it would not be able to take advantage of is_hidden.
        But an is_hiddden flad *could* be added to Campaign if needed.
    """
    entities = cls.query_all_active()
    if featured:
        entities = entities.filter((cls.item_id == m.Item.id) & ~m.Item.is_hidden)
    sorted_entities = sorted(entities.all(), key=(cls.featured_sort_key if featured else cls.sort_key))
    return jsonify({plural: [e.to_dict() for e in sorted_entities]})

@api_blueprint.route('/api/auctions/inactive',
    defaults={'cls': m.Auction, 'plural': 'auctions'},
    methods=['GET'])
@api_blueprint.route('/api/listings/inactive',
    defaults={'cls': m.Listing, 'plural': 'listings'},
    methods=['GET'])
def get_inactive_entities(cls, plural):
    """
    Inactive auctions are auctions that ended.
    Inactive listings are listings that used to be active, but available_quantity reached 0.
    """
    entities = cls.query_all_inactive()
    sorted_entities = sorted(entities.all(), key=cls.sort_key)
    return jsonify({plural: [e.to_dict() for e in sorted_entities]})

@api_blueprint.route('/api/auctions/<key>',
    defaults={'cls': m.Auction, 'singular': 'auction', 'has_item': True},
    methods=['GET', 'PUT', 'DELETE'])
@api_blueprint.route('/api/listings/<key>',
    defaults={'cls': m.Listing, 'singular': 'listing', 'has_item': True},
    methods=['GET', 'PUT', 'DELETE'])
@api_blueprint.route('/api/campaigns/<key>',
    defaults={'cls': m.Campaign, 'singular': 'campaign', 'has_item': False},
    methods=['GET', 'PUT', 'DELETE'])
def get_put_delete_entity(key, cls, singular, has_item):
    user = get_user_from_token(get_token_from_request())
    entity = cls.query.filter_by(key=key).first()
    if not entity:
        return jsonify({'message': "Not found."}), 404

    if request.method == 'GET':
        return jsonify({singular: entity.to_dict(for_user=(user.id if user else None))})
    else:
        is_changing_hidden_state = request.method == 'PUT' and 'is_hidden' in set(request.json.keys())
        is_changing_hidden_state_only = request.method == 'PUT' and set(request.json.keys()) == {'is_hidden'}

        if is_changing_hidden_state and not is_changing_hidden_state_only:
            return jsonify({'message': "When changing hidden state, nothing else can be changed in the same request."}), 400

        if not user:
            return jsonify({'message': "Unauthorized"}), 401
        if is_changing_hidden_state and not user.is_moderator:
            return jsonify({'message': "Unauthorized"}), 401

        if user.id != entity.owner_id and not is_changing_hidden_state:
            return jsonify({'message': "Unauthorized"}), 401

        if isinstance(entity, m.Auction) and not is_changing_hidden_state_only:
            reason = entity.get_not_editable_reason()
            if reason:
                return jsonify({'message': reason}), 403

        if request.method == 'PUT':
            # reorder media, if requested
            if 'media' in request.json:
                for media_item in request.json['media']:
                    media = m.Media.query.filter_by(item_id=entity.item_id, content_hash=media_item['hash']).first()
                    if media:
                        media.index = media_item['index']

            try:
                validated_item = m.Item.validate_dict(request.json, for_method='PUT') if has_item else {}
                validated = cls.validate_dict(request.json, for_method='PUT')
            except m.ValidationError as e:
                return jsonify({'message': e.message}), 400

            for k, v in validated_item.items():
                setattr(entity.item, k, v)
            for k, v in validated.items():
                setattr(entity, k, v)

            nostr = False
            if isinstance(entity, m.Listing) and entity.started:
                user.ensure_stall_key()
                get_nostr_client(user).publish_product(**entity.to_nostr())
                nostr = True

            db.session.commit()

            return jsonify({'nostr': nostr})
        elif request.method == 'DELETE':
            if isinstance(entity, m.Auction | m.Listing):
                for sale in entity.sales:
                    sale.auction = sale.listing = None
                for order_item in m.OrderItem.query.filter_by(listing_id=entity.id):
                    order_item.listing_id = None
            db.session.delete(entity)
            db.session.commit()

            return jsonify({})

@api_blueprint.route('/api/auctions/<key>/media',
    defaults={'cls': m.Auction, 'singular': 'auction'},
    methods=['POST'])
@api_blueprint.route('/api/listings/<key>/media',
    defaults={'cls': m.Listing, 'singular': 'listing'},
    methods=['POST'])
def post_media(key, cls, singular):
    user = get_user_from_token(get_token_from_request())

    if not user:
        return jsonify({'message': "Unauthorized"}), 401

    entity = cls.query.filter_by(key=key).first()
    if not entity:
        return jsonify({'message': "Not found."}), 404

    if user.id != entity.item.seller_id:
        return jsonify({'message': "Unauthorized"}), 401

    if isinstance(entity, m.Auction):
        reason = entity.get_not_editable_reason()
        if reason:
            return jsonify({'message': reason}), 403

    last_index = max([media.index for media in entity.item.media], default=0)
    index = last_index + 1

    added_media = []

    for f in request.files.values():
        media = m.Media(item_id=entity.item_id, index=index)
        if not media.store(get_s3(), f"{singular}_{entity.key}_media_{index}", f.filename, f.read()):
            return jsonify({'message': "Error saving picture!"}), 400
        db.session.add(media)
        index += 1
        added_media.append(media)
    db.session.commit()

    return jsonify({'media': [media.to_dict() for media in added_media]})

@api_blueprint.route('/api/auctions/<key>/media/<content_hash>',
    defaults={'cls': m.Auction},
    methods=['DELETE'])
@api_blueprint.route('/api/listings/<key>/media/<content_hash>',
    defaults={'cls': m.Listing},
    methods=['DELETE'])
def delete_media(key, cls, content_hash):
    user = get_user_from_token(get_token_from_request())

    if not user:
        return jsonify({'message': "Unauthorized"}), 401

    entity = cls.query.filter_by(key=key).first()
    if not entity:
        return jsonify({'message': "Not found."}), 404

    if user.id != entity.item.seller_id:
        return jsonify({'message': "Unauthorized"}), 401

    if isinstance(entity, m.Auction):
        reason = entity.get_not_editable_reason()
        if reason:
            return jsonify({'message': reason}), 403

    media = m.Media.query.filter_by(item_id=entity.item_id, content_hash=content_hash).first()

    if not media:
        return jsonify({'message': "Media not found."}), 404

    db.session.delete(media)
    db.session.commit()

    return jsonify({})

@api_blueprint.route('/api/auctions/<key>/follow', methods=['PUT'])
@user_required
def follow_auction(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404

    follow = bool(request.json['follow'])

    if auction.item.seller_id == user.id and not follow:
        return jsonify({'message': "Can't unfollow your own auctions!"}), 400

    user_auction = m.UserAuction.query.filter_by(user_id=user.id, auction_id=auction.id).one_or_none()
    if user_auction is None:
        message = "Started following the auction."
        user_auction = m.UserAuction(user_id=user.id, auction_id=auction.id, following=follow)
        db.session.add(user_auction)
    else:
        message = "Following the auction." if follow else "Unfollowed the auction."
        user_auction.following = follow
    db.session.commit()

    return jsonify({'message': message})

@api_blueprint.route('/api/auctions/<key>/publish',
    defaults={'cls': m.Auction},
    methods=['PUT'])
@api_blueprint.route('/api/listings/<key>/publish',
    defaults={'cls': m.Listing},
    methods=['PUT'])
@user_required
def put_publish(user, key, cls):
    entity = cls.query.filter_by(key=key).first()
    if not entity:
        return jsonify({'message': "Not found."}), 404

    if entity.item.seller_id != user.id:
        return jsonify({'message': "Unauthorized."}), 401

    if not entity.campaign and not user.wallet:
        return jsonify({'message': "Wallet not configured."}), 400

    entity.start_date = datetime.utcnow()

    if isinstance(entity, m.Auction):
        entity.end_date = entity.start_date + timedelta(hours=entity.duration_hours)

    if isinstance(entity, m.Listing):
        user.ensure_stall_key()
        get_nostr_client(user).publish_product(**entity.to_nostr())

    db.session.commit()

    return jsonify({})

@api_blueprint.route('/api/auctions/<key>/bids', methods=['POST'])
@user_required
def post_bid(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404

    if not auction.started:
        return jsonify({'message': "Auction not started."}), 403
    if auction.ended:
        return jsonify({'message': "Auction ended."}), 403

    amount = int(request.json['amount'])
    if amount > 2100000000:
        # TODO: should we change integer to bigint in the models?
        return jsonify({'message': "Max bidding: 21 BTC!"}), 400

    if not user.twitter_username_verified and not user.nostr_public_key_verified:
        return jsonify({'message': "Please verify your Nostr or Twitter account before bidding!"}), 400

    top_bid = auction.get_top_bid()
    if top_bid and amount <= top_bid.amount:
        return jsonify({'message': f"The top bid is currently {top_bid.amount}. Your bid needs to be higher!"}), 400
    elif amount < auction.starting_bid:
        return jsonify({'message': f"Your bid needs to be equal or higher than {auction.starting_bid}, the starting bid."}), 400

    if auction.campaign: # TODO: for now we only support badges for campaigns
        try:
            btc2usd = btc2fiat.get_value('kraken')
        except Exception:
            return jsonify({'message': "Error fetching the exchange rate!"}), 500
        user_badges = {b['badge'] for b in user.get_badges()}
        for badge, badge_data in app.config['BADGES'].items():
            threshold_sats = usd2sats(badge_data['threshold_usd'], btc2usd)
            if amount >= threshold_sats:
                if badge not in user_badges:
                    return jsonify({'message': f"Can't bid more than ${badge_data['threshold_usd']} without a badge.", 'required_badge': badge}), 402

    if request.json.get('skip_invoice') == 'NEW_BADGE' and any(b['awarded_at'] >= datetime.utcnow() - timedelta(minutes=1) for b in user.get_badges()):
        # NB: we can skip the lightning invoice in the first minute after we have been awarded a badge,
        # this is so that the frontend can automatically re-place the previous bid which failed due to a badge being required
        payment_request = None
        auction.extend()
    else:
        response = get_lnd_client().add_invoice(value=app.config['LND_BID_INVOICE_AMOUNT'], expiry=app.config['LND_BID_INVOICE_EXPIRY'])
        payment_request = response.payment_request

    bid = m.Bid(auction=auction, buyer=user, amount=amount, payment_request=payment_request)
    if payment_request is None:
        bid.settled_at = datetime.utcnow()
    db.session.add(bid)

    started_following = False
    user_auction = m.UserAuction.query.filter_by(user_id=user.id, auction_id=auction.id).one_or_none()
    if user_auction is None:
        user_auction = m.UserAuction(user_id=user.id, auction_id=auction.id, following=True)
        db.session.add(user_auction)
        started_following = True
    else:
        if not user_auction.following:
            started_following = True
            user_auction.following = True
    db.session.commit()

    if payment_request:
        qr = BytesIO()
        pyqrcode.create(payment_request).svg(qr, omithw=True, scale=4)

        return jsonify({
            'payment_request': payment_request,
            'qr': qr.getvalue().decode('utf-8'),
            'messages': [
                "Your bid will be confirmed once you scan the QR code.",
            ] + (["Started following the auction."] if started_following else []),
        })
    else:
        return jsonify({'messages': ["Your bid is confirmed!"]}), 200

@api_blueprint.route('/api/badges/<int:badge>/buy', methods=['PUT'])
@user_required
def buy_badge(user, badge):
    if badge not in app.config['BADGES']:
        return jsonify({'message': "Badge not found."}), 404

    if not request.json.get('campaign_key'):
        # TODO: implement badge purchase without campaign
        return jsonify({'message': "campaign_key is required."}), 400

    campaign = m.Campaign.query.filter_by(key=request.json['campaign_key']).first()
    if not campaign:
        return jsonify({'message': "Campaign not found."}), 404

    try:
        btc2usd = btc2fiat.get_value('kraken')
    except Exception:
        return jsonify({'message': "Error fetching the exchange rate!"}), 500

    try:
        address = campaign.get_new_address()
        db.session.commit()
    except AddressGenerationError as e:
        return jsonify({'message': str(e)}), 500
    except MempoolSpaceError as e:
        return jsonify({'message': str(e)}), 500

    amount_usd = app.config['BADGES'][badge]['price_usd']
    amount_sats = usd2sats(amount_usd, btc2usd)

    sale = m.Sale(
        campaign_id=campaign.id,
        desired_badge=badge,
        buyer_id=user.id,
        address=address,
        price_usd=amount_usd,
        price=amount_sats,
        shipping_domestic=0,
        shipping_worldwide=0,
        quantity=1,
        amount=amount_sats,
        contribution_amount=0,
        contribution_payment_request=None,
        state=m.SaleState.CONTRIBUTION_SETTLED.value)
    db.session.add(sale)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({'message': "Address already in use. Please try again."}), 500

    return jsonify({'sale': sale.to_dict()})

@api_blueprint.route('/api/listings/<key>/buy', methods=['PUT'])
@user_required
def buy_listing(user, key):
    listing = m.Listing.query.filter_by(key=key).first()
    if not listing:
        return jsonify({'message': "Not found."}), 404
    if not listing.started or listing.ended:
        return jsonify({'message': "Listing not active."}), 403

    if m.Sale.query.filter_by(listing_id=listing.id, buyer_id=user.id, state=m.SaleState.REQUESTED.value).first():
        return jsonify({'message': "You already have an active purchase for this listing."}), 403

    # NB: for now the quantity is always 1,
    # but storing this in the DB makes it easy in case we want to change this later on:
    # it would just be a matter of getting a quantity from the UI and sending it here to be used instead of 1.
    quantity = 1

    if listing.available_quantity < quantity:
        return jsonify({'message': "Not enough items in stock!"}), 400

    # NB: here we "lock" the quantity. it is given back if the sale expires
    listing.available_quantity -= quantity

    try:
        btc2usd = btc2fiat.get_value('kraken')
    except Exception:
        return jsonify({'message': "Error fetching the exchange rate!"}), 500

    try:
        if listing.campaign:
            address = listing.campaign.get_new_address()
        else:
            address = listing.item.seller.get_new_address()
    except AddressGenerationError as e:
        return jsonify({'message': str(e)}), 500
    except MempoolSpaceError as e:
        return jsonify({'message': str(e)}), 500

    price_sats = usd2sats(listing.price_usd, btc2usd)
    contribution_amount = listing.item.seller.get_contribution_amount(price_sats * quantity)

    if contribution_amount != 0:
        response = get_lnd_client().add_invoice(value=contribution_amount, expiry=app.config['LND_CONTRIBUTION_INVOICE_EXPIRY_LISTING'])
        contribution_payment_request = response.payment_request
    else:
        contribution_payment_request = None

    sale = m.Sale(item_id=listing.item.id, listing_id=listing.id,
        buyer_id=user.id,
        address=address,
        price_usd=listing.price_usd,
        price=price_sats,
        shipping_domestic=usd2sats(listing.item.shipping_domestic_usd, btc2usd),
        shipping_worldwide=usd2sats(listing.item.shipping_worldwide_usd, btc2usd),
        quantity=quantity,
        amount=(price_sats * quantity) - contribution_amount,
        contribution_amount=contribution_amount,
        contribution_payment_request=contribution_payment_request)
    if not contribution_payment_request:
        sale.state = m.SaleState.CONTRIBUTION_SETTLED.value
    db.session.add(sale)

    try:
        db.session.commit()
    except IntegrityError:
        return jsonify({'message': "Address already in use. Please try again."}), 500

    return jsonify({'sale': sale.to_dict()})

@api_blueprint.route("/api/users/<nym>/auctions",
    defaults={'plural': 'auctions'},
    methods=['GET'])
@api_blueprint.route("/api/users/<nym>/listings",
    defaults={'plural': 'listings'},
    methods=['GET'])
@api_blueprint.route("/api/users/<nym>/campaigns",
    defaults={'plural': 'campaigns'},
    methods=['GET'])
def get_user_entities(nym, plural):
    for_user = get_user_from_token(get_token_from_request())
    for_user_id = for_user.id if for_user else None

    if nym == 'me':
        user = for_user
    else:
        user = m.User.query.filter_by(nym=nym).first()

    if not user:
        return jsonify({'message': "User not found."}), 404

    def iter_entities():
        if plural == 'campaigns':
            for campaign in user.campaigns:
                yield campaign
        else:
            for item in user.items:
                for entity in getattr(item, plural):
                    yield entity

    entities = {}
    for entity in iter_entities():
        if entity.filter_state(request.args.get('filter'), for_user_id):
            entities[f"{plural}_{entity.id}"] = entity

    sorted_entities = sorted(entities.values(), key=lambda l: l.created_at, reverse=True)

    return jsonify({plural: [e.to_dict(for_user=for_user_id) for e in sorted_entities]})

@api_blueprint.route("/api/campaigns/<key>/auctions",
    defaults={'plural': 'auctions'},
    methods=['GET'])
@api_blueprint.route("/api/campaigns/<key>/listings",
    defaults={'plural': 'listings'},
    methods=['GET'])
def get_campaign_entities(key, plural):
    for_user = get_user_from_token(get_token_from_request())
    for_user_id = for_user.id if for_user else None

    campaign = m.Campaign.query.filter_by(key=key).first()

    if not campaign:
        return jsonify({'message': "Campaign not found."}), 404

    entities = []
    for entity in getattr(campaign, plural):
        if entity.filter_state(request.args.get('filter'), for_user_id):
            entities.append(entity)
    sorted_entities = sorted(entities, key=lambda e: e.created_at, reverse=True)

    return jsonify({plural: [e.to_dict(for_user=for_user_id) for e in sorted_entities]})

@api_blueprint.route("/api/campaigns/<key>/avatars/featured",
    methods=['GET'])
def get_campaign_featured_avatars(key):
    campaign = m.Campaign.query.filter_by(key=key).first()

    if not campaign:
        return jsonify({'message': "Campaign not found."}), 404

    avatars = {'auction_avatars': [], 'listing_avatars': []}

    for which_avatars, entities in [('auction_avatars', campaign.auctions), ('listing_avatars', campaign.listings)]:
        for entity in entities:
            if entity.started and not entity.item.is_hidden:
                avatar = {
                    'url': entity.item.seller.profile_image_url,
                    'entity_key': entity.key,
                    'featured_sort_key': entity.featured_sort_key()
                }
                avatars[which_avatars].append(avatar)
        avatars[which_avatars].sort(key=lambda a: a['featured_sort_key'], reverse=True)

        # NB: we do unique after we have sorted,
        # so an avatar is shown on the position of its highest scoring auction/listing if it has multiple!
        unique_avatars = []
        seen_avatars = set()
        for avatar in avatars[which_avatars]:
            if avatar['url'] not in seen_avatars:
                seen_avatars.add(avatar['url'])
                unique_avatars.append(avatar)
        avatars[which_avatars] = unique_avatars

    return jsonify(avatars)

@api_blueprint.route("/api/relays", methods=['GET'])
def get_relays():
    return jsonify({'relays': [{'url': r.url} for r in m.Relay.query.all()]})

@api_blueprint.route("/api/stalls/<pubkey>", methods=['GET'])
def get_stall(pubkey):
    seller = m.User.query.filter_by(stall_public_key=pubkey).one_or_none()
    if not seller:
        return jsonify({'message': "Stall not found!"}), 404

    return jsonify({'name': seller.stall_name, 'description': seller.stall_description})

@api_blueprint.route("/api/stalls/<pubkey>/events", methods=['POST'])
def post_stall_event(pubkey):
    seller = m.User.query.filter_by(stall_public_key=pubkey).one_or_none()
    if not seller:
        return jsonify({'message': "Stall not found!"}), 404

    if request.json['kind'] == 4:
        # TODO: validate sig?

        sk = PrivateKey(bytes.fromhex(seller.stall_private_key))
        cleartext_content = json.loads(sk.decrypt_message(request.json['content'], public_key_hex=request.json['pubkey']))

        if int(cleartext_content['type']) == 0:
            if m.Order.query.filter_by(uuid=cleartext_content['id']).one_or_none():
                return jsonify({'message': "Order already exists!"}), 409

            try:
                payment_address = seller.get_new_address()
            except AddressGenerationError as e:
                return jsonify({'message': str(e)}), 500
            except MempoolSpaceError as e:
                return jsonify({'message': str(e)}), 500

            order = m.Order(
                uuid=cleartext_content['id'],
                event_id=request.json['id'],
                buyer_public_key=request.json['pubkey'],
                requested_at=datetime.utcfromtimestamp(request.json['created_at']),
                payment_address=payment_address)
            db.session.add(order)
            db.session.commit()

            for item in cleartext_content['items']:
                listing = m.Listing.query.filter_by(key=item['product_id']).first()

                quantity = item['quantity']

                if listing.available_quantity < quantity:
                    # TODO: reply to buyer with a DM?
                    return jsonify({'message': "Not enough items in stock!"}), 400

                # NB: here we "lock" the quantity. it is given back if the order expires
                listing.available_quantity -= quantity

                order_item = m.OrderItem(order_id=order.id, item_id=listing.item_id, listing_id=listing.id, quantity=quantity)
                db.session.add(order_item)
                db.session.commit()

                order.total_usd += listing.price_usd * quantity

            try:
                btc2usd = btc2fiat.get_value('kraken')
            except Exception:
                return jsonify({'message': "Error fetching the exchange rate!"}), 500

            order.total = usd2sats(order.total_usd, btc2usd)

            db.session.commit()

            get_nostr_client(seller).send_dm(
                order.buyer_public_key,
                json.dumps({
                    'id': order.uuid,
                    'type': 1,
                    'message': f"Please send the amount directly to the seller.",
                    'payment_options': [{'type': 'btc', 'link': order.payment_address}]
            }))

    return jsonify({})
