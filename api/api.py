import bleach
import btc2fiat
from datetime import datetime, timedelta
import ecdsa
from ecdsa.keys import BadSignatureError
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, jsonify, request
from hashlib import sha256
from io import BytesIO
import json
import jwt
import lnurl
import pyqrcode
import secrets
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
import time

from extensions import db
import models as m
from main import app, get_birdwatcher, get_lndhub_client, get_s3, get_site_admin_config
from main import get_token_from_request, get_user_from_token, user_required
from main import MempoolSpaceError
from nostr_utils import EventValidationError, validate_event
from utils import usd2sats, sats2usd, parse_xpub, UnknownKeyTypeError

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api/healthcheck', methods=['GET'])
def healthcheck(): # TODO: I don't really like this, for some reason, but it is used in "dev" mode by docker-compose
    return jsonify({'success': True})

@api_blueprint.route('/api/login/lnurl', methods=['GET'])
def auth_lnurl():
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
        return jsonify({'message': "User not found. Please create an account first."}), 400
    db.session.delete(lnauth)
    db.session.commit()

    if not user.nostr_public_key:
        return jsonify({'message': "This is an old style Plebeian Market account that doesn't have a Nostr identity associated. Please log in using Nostr instead!", 'nostr_required': True}), 403

    token_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=app.config['JWT_EXPIRE_DAYS']),
        'r': secrets.token_hex(4), # just 4 random bytes, to ensure the tokens are unique (mostly for tests)
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token, 'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/login/nostr', methods=['PUT'])
def auth_nostr():
    try:
        validate_event(request.json)
    except Exception:
        return jsonify({'message': "Invalid event."}), 400

    if request.json['kind'] != 1 or request.json['content'] != "Plebeian Market Login":
        return jsonify({'message': "Invalid event."}), 400

    pubkey = request.json['pubkey']

    user = m.User.query.filter_by(nostr_public_key=pubkey).first()

    if not user:
        user = m.User(nostr_public_key=pubkey)
        user.ensure_merchant_key()
        db.session.add(user)
        db.session.commit()

    token_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=app.config['JWT_EXPIRE_DAYS']),
        'r': secrets.token_hex(4), # just 4 random bytes, to ensure the tokens are unique (mostly for tests)
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token, 'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/users/me', methods=['GET'])
@user_required
def get_me(user):
    return jsonify({'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/users/me', methods=['PUT'])
@user_required
def put_me(user: m.User):
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

    if 'lnauth_key_name' in request.json:
        user.lnauth_key_name = request.json['lnauth_key_name']

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
            user.generate_verification_phrase('email')
            user.send_email_verification()

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

    if 'contribution_percent' in request.json:
        user.contribution_percent = request.json['contribution_percent']

    if 'wallet' in request.json:
        if request.json.get('wallet'):
            try:
                k = parse_xpub(request.json['wallet'])
            except UnknownKeyTypeError as e:
                return jsonify({'message': "Invalid wallet."}), 400
            try:
                _ = k.subkey(0).subkey(0).address()
            except AttributeError:
                return jsonify({'message': "Invalid wallet."}), 400
            user.wallet = request.json['wallet']
            user.wallet_index = 0
            user.wallet_name = request.json.get('wallet_name')
        else:
            user.wallet = user.wallet_name = None
            user.wallet_index = 0

    if 'lightning_address' in request.json:
        if "@" not in request.json['lightning_address']:
            return jsonify({'message': "Invalid lightning address."}), 400
        user.lightning_address = request.json['lightning_address']

    published_to_nostr = False
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
        user.ensure_merchant_key()
        if user.stall_name:
            birdwatcher = get_birdwatcher()
            user.stall_nostr_event_id = birdwatcher.publish_stall(user)
            if not user.stall_nostr_event_id:
                app.logger.error(f"Error publishing Nostr stall for user id={user.id}")
                return jsonify({'message': "Error publishing stall to Nostr!"}), 500
            if not birdwatcher.publish_merchant_metadata(user):
                # NB: this is a non-critical error - everything works just fine without the metadata,
                # except the merchant would not have a "friendly name". so we just log the error and ignore!
                app.logger.error(f"Error publishing merchant metadata for user id={user.id}")
            published_to_nostr = True
        else:
            published_to_nostr = False

    try:
        db.session.commit()
    except IntegrityError:
        app.logger.exception(f"Error while saving user profile. {user.id=}")

        # there are very few cases where this could happen
        # namely with some old users that were created before we started saving the "clean" version of nym / twitter in the DB
        return jsonify({'message': "Please retry or contact support!"}), 500

    return jsonify({'user': user.to_dict(for_user=user.id), 'published_to_nostr': published_to_nostr})

@api_blueprint.route("/api/users/me/verify/email", methods=['PUT'])
@user_required
def verify_email(user: m.User):
    if request.json.get('resend'):
        if user.email_verification_phrase_sent_at and user.email_verification_phrase_sent_at >= datetime.utcnow() - timedelta(minutes=1):
            return jsonify({'message': "Please wait at least one minuted before requesting a new verification phrase!"}), 400
        user.generate_verification_phrase('email')
        user.send_email_verification()
        db.session.commit()
        return jsonify({})

    if not request.json.get('phrase'):
        return jsonify({'message': "Please provide the verification phrase!"}), 400

    if user.email_verification_phrase_check_counter > 5:
        return jsonify({'message': "Please try requesting a new verification phrase!"}), 400

    clean_phrase = ' '.join([w for w in request.json['phrase'].lower().split(' ') if w])

    if user.email_verification_phrase == clean_phrase:
        user.email_verified = True
        db.session.commit()
        return jsonify({})
    else:
        time.sleep(2 ** user.email_verification_phrase_check_counter)
        user.email_verification_phrase_check_counter += 1
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
            return jsonify({'message': "This wallet is already associated with another Plebeian Market user!", 'user_exists': True}), 400
    else:
        # waiting for the user to scan the QR code...
        return jsonify({'success': False})

@api_blueprint.route("/api/users/me/migrate", methods=['PUT'])
@user_required
def migrate_user(user):
    old_user = m.User.query.filter_by(lnauth_key=user.new_lnauth_key).first()
    for old_item in old_user.items:
        item = m.Item(seller=user,
                      title=old_item.title, description=old_item.description,
                      extra_shipping_domestic_usd=old_item.extra_shipping_domestic_usd, extra_shipping_worldwide_usd=old_item.extra_shipping_worldwide_usd)
        db.session.add(item)
        db.session.commit()
        for old_media in old_item.media:
            media = m.Media(item_id=item.id, index=old_media.index, content_hash=old_media.content_hash, url=old_media.url)
            db.session.add(media)
        for old_listing in old_item.listings:
            listing = m.Listing(item_id=item.id,
                                start_date=old_listing.start_date,
                                price_usd=old_listing.price_usd, available_quantity=old_listing.available_quantity)
            listing.generate_key()
            db.session.add(listing)
    db.session.commit()

    old_user.lnauth_key = None
    old_user.migrated_at = datetime.utcnow()
    old_user.migrated_to_user_id = user.id
    db.session.commit()

    user.lnauth_key = user.new_lnauth_key

    db.session.commit()

    if not get_birdwatcher().publish_badge_award(app.config['BADGE_DEFINITION_OG']['badge_id'], user.nostr_public_key):
        app.logger.warning(f"Failed to publish badge award for {user.nostr_public_key}")

    return jsonify({})

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
            if not get_birdwatcher().add_relay(relay.url):
                return jsonify({'message': "Error subscribing to relay."}), 500
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

@api_blueprint.route('/api/users/me/orders', methods=['GET'])
@user_required
def get_orders(user):
    orders = m.Order.query.filter_by(seller_id=user.id).order_by(desc(m.Order.requested_at)).all()

    return jsonify({'orders': [o.to_dict() for o in orders]})

@api_blueprint.route('/api/users/me/orders/<uuid>', methods=['PUT'])
@user_required
def put_order(user, uuid):
    order = m.Order.query.filter_by(seller_id=user.id, uuid=uuid).one_or_none()

    if not order:
        return jsonify({'message': "Not found."}), 404

    message = None

    if request.json.get('paid'):
        message = "The seller accepted your payment!"
        order.paid_at = datetime.utcnow()

    if request.json.get('shipped'):
        message = "Your order was shipped!"
        order.shipped_at = datetime.utcnow()
    elif request.json.get('shipped') == False:
        message = "Your order was not shipped!"
        order.shipped_at = None

    if request.json.get('canceled'):
        message = "Your order was canceled by the seller!"
        order.canceled_at = datetime.utcnow()

    if request.json.get('expired') == False:
        message = "Your order was marked as active by the seller!"
        order.expired_at = None

    if not get_birdwatcher().send_dm(order.seller.parse_merchant_private_key(), order.buyer_public_key,
        json.dumps({'id': order.uuid, 'type': 2, 'paid': order.paid_at is not None, 'shipped': order.shipped_at is not None, 'message': message})):
        return jsonify({'message': "Error sending Nostr reply to the buyer."}), 500

    db.session.commit()

    return jsonify({'order': order.to_dict()})

@api_blueprint.route("/api/users/me/auctions",
    defaults={'cls': m.Auction, 'singular': 'auction'},
    methods=['POST'])
@api_blueprint.route("/api/users/me/listings",
    defaults={'cls': m.Listing, 'singular': 'listing'},
    methods=['POST'])
@user_required
def post_entity(user, cls, singular):
    for k in cls.REQUIRED_FIELDS:
        if k not in request.json:
            return jsonify({'message': f"Missing key: {k}."}), 400

    try:
        validated_item = m.Item.validate_dict(request.json)
        validated_entity = cls.validate_dict(request.json)
    except m.ValidationError as e:
        return jsonify({'message': e.message}), 400

    item = m.Item(seller=user, **validated_item)
    db.session.add(item)
    db.session.commit()
    for cat in request.json.get('categories', []):
        category_tag = m.Category.tag_from_str(cat)
        category = m.Category.query.filter_by(tag=category_tag).first()
        if category is None:
            category = m.Category(tag=category_tag)
            db.session.add(category)
            db.session.commit()
        item_category = m.ItemCategory(item_id=item.id, category_id=category.id)
        db.session.add(item_category)
        db.session.commit()

    entity = cls(**validated_entity)
    entity.generate_key()

    if item:
        entity.item = item

    db.session.add(entity)
    db.session.commit()

    return jsonify({'key': entity.key, singular: entity.to_dict(for_user=user.id)})

@api_blueprint.route('/api/auctions/active',
    defaults={'cls': m.Auction, 'plural': 'auctions'},
    methods=['GET'])
@api_blueprint.route('/api/listings/active',
    defaults={'cls': m.Listing, 'plural': 'listings'},
    methods=['GET'])
def get_entities(cls, plural):
    """
    Active auctions are all auctions currently running.
    Active listings are all listings that have been published and are still available for sale.
    """
    entities = cls.query_all_active()
    sorted_entities = sorted(entities.all(), key=cls.sort_key)
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
    defaults={'cls': m.Auction, 'singular': 'auction'},
    methods=['GET', 'PUT', 'DELETE'])
@api_blueprint.route('/api/listings/<key>',
    defaults={'cls': m.Listing, 'singular': 'listing'},
    methods=['GET', 'PUT', 'DELETE'])
def get_put_delete_entity(key, cls, singular):
    user = get_user_from_token(get_token_from_request())
    entity = cls.query.filter_by(key=key).first()
    if not entity:
        return jsonify({'message': "Not found."}), 404

    if request.method == 'GET':
        return jsonify({singular: entity.to_dict(for_user=(user.id if user else None))})
    else:
        if not user or user.id != entity.owner_id:
            return jsonify({'message': "Unauthorized"}), 401

        if isinstance(entity, m.Auction):
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
                validated_item = m.Item.validate_dict(request.json)
                validated = cls.validate_dict(request.json)
            except m.ValidationError as e:
                return jsonify({'message': e.message}), 400

            for k, v in validated_item.items():
                setattr(entity.item, k, v)
            for k, v in validated.items():
                setattr(entity, k, v)

            existing_cats = entity.item.category_tags
            seen_category_tags = set()
            for cat in request.json.get('categories', []):
                category_tag = m.Category.tag_from_str(cat)
                seen_category_tags.add(category_tag)
                if category_tag not in existing_cats:
                    category = m.Category.query.filter_by(tag=category_tag).first()
                    if category is None:
                        category = m.Category(tag=category_tag)
                        db.session.add(category)
                        db.session.commit()
                    item_category = m.ItemCategory(item_id=entity.item.id, category_id=category.id)
                    db.session.add(item_category)
                    db.session.commit()
            for cat_tag in existing_cats:
                if cat_tag not in seen_category_tags:
                    category = m.Category.query.filter_by(tag=cat_tag).first()
                    item_category = m.ItemCategory.query.filter_by(item_id=entity.item.id, category_id=category.id).first()
                    db.session.delete(item_category)

            if (isinstance(entity, m.Auction) or isinstance(entity, m.Listing)) and entity.started:
                user.ensure_merchant_key()
                entity.nostr_event_id = get_birdwatcher().publish_product(entity)
                if not entity.nostr_event_id:
                    return jsonify({'message': "Error publishing product to Nostr!"}), 500

            db.session.commit()

            return jsonify({'nostr_event_id': entity.nostr_event_id})
        elif request.method == 'DELETE':
            if isinstance(entity, m.Listing):
                for order_item in m.OrderItem.query.filter_by(listing_id=entity.id):
                    order_item.listing_id = None
            if isinstance(entity, m.Auction):
                for order_item in m.OrderItem.query.filter_by(auction_id=entity.id):
                    order_item.auction_id = None
            if not get_birdwatcher().delete_product(entity):
                return jsonify({'message': "Error deleting item from Nostr!"}), 500
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

    if entity.started:
        entity.nostr_event_id = get_birdwatcher().publish_product(entity, added_media)
        if not entity.nostr_event_id:
            return jsonify({'message': "Error publishing product to Nostr!"}), 500

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

    user.ensure_merchant_key()
    entity.nostr_event_id = get_birdwatcher().publish_product(entity)
    if not entity.nostr_event_id:
        return jsonify({'message': "Error publishing product to Nostr!"}), 500

    db.session.commit()

    return jsonify({})

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

    if app.config['ENV'] in ('staging', 'prod'):
        site_admin_nostr_public_key = get_site_admin_config()['nostr_private_key'].public_key.hex()
        site_admin = m.User.query.filter_by(nostr_public_key=site_admin_nostr_public_key).first()
        if not site_admin:
            return jsonify({'message': "Site not configured!"}), 500

    if entity.item.seller_id != user.id:
        return jsonify({'message': "Unauthorized."}), 401

    if not user.wallet and not user.lightning_address:
        return jsonify({'message': "Wallet not configured."}), 400

    entity.start_date = datetime.utcnow()

    if isinstance(entity, m.Auction):
        entity.end_date = entity.start_date + timedelta(hours=entity.duration_hours)

    user.ensure_merchant_key()
    entity.nostr_event_id = get_birdwatcher().publish_product(entity)
    if not entity.nostr_event_id:
        return jsonify({'message': "Error publishing product to Nostr!"}), 500

    db.session.commit()

    return jsonify({})

@api_blueprint.route("/api/users/<nym>/auctions",
    defaults={'plural': 'auctions'},
    methods=['GET'])
@api_blueprint.route("/api/users/<nym>/listings",
    defaults={'plural': 'listings'},
    methods=['GET'])
def get_user_entities(nym, plural):
    for_user = get_user_from_token(get_token_from_request())
    for_user_id = for_user.id if for_user else None
    user = for_user if nym == 'me' else m.User.query.filter_by(nym=nym).first()

    if not user:
        return jsonify({'message': "User not found."}), 404

    def iter_entities():
        for item in user.items:
            for entity in getattr(item, plural):
                yield entity

    entities = {}
    for entity in iter_entities():
        if entity.filter_state(request.args.get('filter'), for_user_id):
            entities[f"{plural}_{entity.id}"] = entity

    sorted_entities = sorted(entities.values(), key=lambda l: l.created_at, reverse=True)

    return jsonify({plural: [e.to_dict(for_user=for_user_id) for e in sorted_entities]})

@api_blueprint.route("/api/relays", methods=['GET'])
def get_relays():
    if app.config['ENV'] in ('test', 'dev'):
        relay_urls = ["ws://relay:7777"]
    else:
        relay_urls = [r.url for r in m.Relay.query.all()]
    return jsonify({'relays': [{'url': url} for url in relay_urls]})

@api_blueprint.route("/api/keys/<pubkey>/metadata", methods=['GET'])
def query_metadata(pubkey):
    return jsonify(get_birdwatcher().query_metadata(pubkey))

@api_blueprint.route("/api/merchants/<pubkey>", methods=['GET'])
def get_merchant(pubkey):
    seller = m.User.query.filter_by(merchant_public_key=pubkey).one_or_none()
    if not seller:
        return jsonify({'message': "Merchant not found!"}), 404

    # NB: a merchant can currently only have one stall, but this will change
    return jsonify({'stalls': [{'name': seller.stall_name, 'description': seller.stall_description}]})

@api_blueprint.route("/api/merchants", methods=['GET'])
def get_merchants():
    sellers = []
    for user in m.User.query.all():
        if user.merchant_public_key:
            # NB: a merchant can currently only have one stall, but this will change
            sellers.append({'public_key': user.merchant_public_key, 'stalls': [{'name': user.stall_name, 'description': user.stall_description}]})
    return jsonify(sellers)

@api_blueprint.route("/api/merchants/<pubkey>/messages", methods=['POST'])
def post_merchant_message(pubkey):
    try:
        validate_event(request.json)
    except EventValidationError as e:
        return jsonify({'message': e.message}), 400

    merchant = m.User.query.filter_by(merchant_public_key=pubkey).one_or_none()
    if not merchant:
        return jsonify({'message': "Merchant not found!"}), 404

    merchant_private_key = merchant.parse_merchant_private_key()

    if request.json['kind'] != 4:
        # this should not happen as the birdwatcher already filters DMs
        app.logger.warning("Received a non-DM as a merchant message. Ignoring.")
        return jsonify({})

    cleartext_content = None
    try:
        cleartext_content = json.loads(merchant_private_key.decrypt_message(request.json['content'], public_key_hex=request.json['pubkey']))
    except json.decoder.JSONDecodeError:
        app.logger.info("DM content is not JSON. Ignoring.")
        return jsonify({})

    if 'type' not in cleartext_content:
        app.logger.info("Missing message type. Ignoring.")
        return jsonify({})

    message_type = None
    try:
        message_type = int(cleartext_content['type'])
    except (TypeError, ValueError):
        app.logger.info("Invalid message type. Ignoring.")
        return jsonify({})

    if message_type != 0:
        app.logger.info("Message is not an order request. Ignoring.")
        return jsonify({})

    if 'id' not in cleartext_content:
        message = "Invalid order: missing id."
        get_birdwatcher().send_dm(merchant_private_key, request.json['pubkey'], message)
        return jsonify({'message': message}), 400

    if 'shipping_id' not in cleartext_content:
        message = "Invalid order: missing shipping zone."
        get_birdwatcher().send_dm(merchant_private_key, request.json['pubkey'],
            json.dumps({'id': cleartext_content['id'], 'type': 2, 'paid': False, 'shipped': False, 'message': message}))
        return jsonify({'message': message}), 400

    order = m.Order.query.filter_by(uuid=cleartext_content['id']).one_or_none()

    if order and order.buyer_public_key != request.json['pubkey']:
        return jsonify({'message': "Not allowed!"}), 403

    if order and (order.paid_at or order.shipped_at or order.expired_at or order.canceled_at):
        return jsonify({'message': "Order already exists and it is paid, shipped, expired or canceled!"}), 409

    try:
        btc2usd = btc2fiat.get_value('kraken')
    except Exception:
        return jsonify({'message': "Error fetching the exchange rate!"}), 500

    shipping_domestic_id = sha256(merchant.shipping_from.encode('utf-8')).hexdigest() if merchant.shipping_from else ""

    shipping_usd = None
    shipping_id = cleartext_content['shipping_id']
    if shipping_id == 'WORLD':
        shipping_usd = merchant.shipping_worldwide_usd
    elif shipping_id == shipping_domestic_id:
        shipping_usd = merchant.shipping_domestic_usd
    else:
        message = "Invalid shipping zone!"
        get_birdwatcher().send_dm(merchant_private_key, request.json['pubkey'],
            json.dumps({'id': cleartext_content['id'], 'type': 2, 'paid': False, 'shipped': False, 'message': message}))
        return jsonify({'message': message}), 400

    if not order:
        if merchant.wallet:
            try:
                on_chain_address = merchant.get_new_address()
            except m.AddressGenerationError as e:
                return jsonify({'message': str(e)}), 500
            except MempoolSpaceError as e:
                return jsonify({'message': str(e)}), 500
        else:
            on_chain_address = None
        lightning_address = merchant.lightning_address

        order_listings = [] # [(listing, quantity), ...]
        for item in cleartext_content.get('items', []):
            # NB: we only look for listings here. auction orders are generated in finalize-auctions!
            listing = m.Listing.query.filter_by(uuid=item['product_id']).first()
            if listing:
                if not listing.started or listing.ended:
                    message = "Listing not active."
                    get_birdwatcher().send_dm(merchant_private_key, request.json['pubkey'],
                        json.dumps({'id': cleartext_content['id'], 'type': 2, 'paid': False, 'shipped': False, 'message': message}))
                    return jsonify({'message': message}), 403
                if listing.available_quantity is not None and listing.available_quantity < item['quantity']:
                    message = "Not enough items in stock!"
                    get_birdwatcher().send_dm(merchant_private_key, request.json['pubkey'],
                        json.dumps({'id': cleartext_content['id'], 'type': 2, 'paid': False, 'shipped': False, 'message': message}))
                    return jsonify({'message': message}), 400
                order_listings.append((listing, item['quantity']))

        if len(order_listings) == 0:
            message = "Empty order!"
            get_birdwatcher().send_dm(merchant_private_key, request.json['pubkey'],
                json.dumps({'id': cleartext_content['id'], 'type': 2, 'paid': False, 'shipped': False, 'message': message}))
            return jsonify({'message': message}), 400

        order = m.Order(
            uuid=cleartext_content['id'],
            seller_id=merchant.id,
            event_id=request.json['id'],
            buyer_public_key=request.json['pubkey'],
            buyer_name=cleartext_content.get('name'),
            buyer_address=cleartext_content.get('address'),
            buyer_message=cleartext_content.get('message'),
            buyer_contact=cleartext_content.get('contact'),
            requested_at=datetime.utcnow(),
            on_chain_address=on_chain_address,
            lightning_address=lightning_address)
        db.session.add(order)
        db.session.commit()

        for listing, quantity in order_listings:
            if listing.available_quantity is not None:
                # here we "lock" the quantity. it is given back if the order expires
                listing.available_quantity -= quantity
                # NB: we need to update the quantity in Nostr as well!
                listing.nostr_event_id = get_birdwatcher().publish_product(listing)

            order_item = m.OrderItem(order_id=order.id, item_id=listing.item_id, listing_id=listing.id, quantity=quantity)
            db.session.add(order_item)

            if shipping_id == 'WORLD':
                shipping_usd += listing.item.extra_shipping_worldwide_usd * quantity
            elif shipping_id == shipping_domestic_id:
                shipping_usd += listing.item.extra_shipping_domestic_usd * quantity

            order.total_usd += listing.price_usd * quantity

        order.shipping_usd = shipping_usd

        order.total_usd += order.shipping_usd
        order.total = usd2sats(order.total_usd, btc2usd)

        app.logger.info(f"New order for merchant {pubkey}: {order.uuid=} {len(order_listings)} items, {order.total_usd=}, {order.total=}!")
    else: # order exists, so we can edit it here
        # NB: this is mostly used for orders where the item bought is an auction,
        # which are generated by us in finalize-auctions and the client will re-submit the order to add their name/address/etc
        # but in theory this could be used for any orders as long as they are not already paid/shipped/expired/canceled!
        order.buyer_name = cleartext_content.get('name')
        order.buyer_address = cleartext_content.get('address')
        order.buyer_message = cleartext_content.get('message')
        order.buyer_contact = cleartext_content.get('contact')

        order.total = order.total_usd = 0

        listing_count = 0
        auction_count = 0
        for order_item in order.order_items:
            if order_item.listing_id:
                listing = m.Listing.query.filter_by(id=order_item.listing_id).first()
                order.total_usd += listing.price_usd * order_item.quantity
                listing_count += 1
            elif order_item.auction_id:
                auction = m.Auction.query.filter_by(id=order_item.auction_id).first()
                winning_bid = auction.get_winning_bid()
                order.total += winning_bid.amount
                auction_count += 1

            if shipping_id == 'WORLD':
                shipping_usd += order_item.item.extra_shipping_worldwide_usd * order_item.quantity
            elif shipping_id == shipping_domestic_id:
                shipping_usd += order_item.item.extra_shipping_domestic_usd * order_item.quantity

        order.shipping_usd = shipping_usd

        if order.total_usd:
            order.total_usd += order.shipping_usd
            order.total = usd2sats(order.total_usd, btc2usd)
        else:
            order.total += usd2sats(order.shipping_usd, btc2usd)
            order.total_usd = sats2usd(order.total, btc2usd)

        app.logger.info(f"Edited order for merchant {pubkey}: {order.uuid=} {listing_count} listings, {auction_count} auctions, {order.total_usd=}, {order.total=}!")

    payment_options = []

    if order.on_chain_address:
        payment_options.append({'type': 'btc', 'link': order.on_chain_address, 'amount_sats': order.total})

    if order.lightning_address:
        lndhub_client = get_lndhub_client()
        invoice_information = lndhub_client.create_invoice(order.id, order.total)

        if not invoice_information:
            app.logger.info(f"Error while trying to create_invoice. Retrying...")
            time.sleep(5)
            lndhub_client.get_login_token()
            invoice_information = lndhub_client.create_invoice(order.id, order.total)

        if invoice_information and invoice_information['payment_request']:
            lightning_invoice = m.LightningInvoice(
                order_id=order.id,
                invoice=invoice_information['payment_request'],
                payment_hash=invoice_information['payment_hash'],
                price=order.total,
                expires_at=invoice_information['expires_at']
            )
            db.session.add(lightning_invoice)
            db.session.commit()

            payment_options.append({'type': 'ln', 'link': invoice_information['payment_request'], 'amount_sats': order.total})

        else:
            return jsonify({'message': "Error sending the payment options back to the buyer (couldn't create a new LN invoice)"}), 500

    if not get_birdwatcher().send_dm(merchant_private_key, order.buyer_public_key,
        json.dumps({
            'id': order.uuid,
            'type': 1,
            'message': f"Please send the {order.total} sats ({1 / app.config['SATS_IN_BTC'] * order.total :.9f} BTC) directly to the seller.",
            'payment_options': payment_options})):
        return jsonify({'message': "Error sending the payment options back to the buyer (couldn't send the nostr type=1 message)"}), 500

    db.session.commit()

    return jsonify({})

@api_blueprint.route("/api/merchants/<merchant_pubkey>/auctions/<auction_event_id>/bids", methods=['POST'])
def post_auction_bid(merchant_pubkey, auction_event_id):
    try:
        validate_event(request.json)
    except EventValidationError as e:
        return jsonify({'message': e.message}), 400

    merchant = m.User.query.filter_by(merchant_public_key=merchant_pubkey).one_or_none()
    if not merchant:
        return jsonify({'message': "Merchant not found!"}), 404

    auction = m.Auction.query.filter(m.Item.id == m.Auction.item_id, m.Item.seller_id == merchant.id).filter_by(nostr_event_id=auction_event_id).one_or_none()
    if not auction:
        return jsonify({'message': "Auction not found!"}), 404

    birdwatcher = get_birdwatcher()

    if request.json['pubkey'] == merchant_pubkey:
        message = "Cannot bid on one's own auction!"
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400

    try:
        amount = int(request.json['content'])
    except TypeError:
        message = "Invalid bid amount!"
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400

    if not auction.started:
        message = "Auction not started."
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400
    if auction.ended:
        message = "Auction ended."
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400

    if amount > 2100000000:
        message = "Max bidding: 21 BTC!"
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400

    top_bid = auction.get_top_bid()

    if top_bid and amount <= top_bid.amount:
        message = f"Amount needs to be higher than the previous top bid!"
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400
    elif amount < auction.starting_bid:
        message = f"Amount needs to be at least {auction.starting_bid}, the starting bid."
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400

    buyer_metadata = birdwatcher.query_metadata(request.json['pubkey'])
    if len(buyer_metadata['verified_identities']) < app.config['BID_REQUIRED_VERIFIED_IDENTITIES_COUNT']:
        message = f"User needs at least {app.config['BID_REQUIRED_VERIFIED_IDENTITIES_COUNT']} verified external identities in order to bid!"
        app.logger.info(f"{message} pubkey={request.json['pubkey']} verified_identities={buyer_metadata['verified_identities']}")
        birdwatcher.publish_bid_status(auction, request.json['id'], 'rejected', message)
        return jsonify({'message': message}), 400

    is_settled = True
    if auction.skin_in_the_game_required and amount > auction.reserve_bid:
        has_skin_in_the_game = False
        # TODO: optimize query - join tables
        for order in m.Order.query.filter(m.Order.buyer_public_key == request.json['pubkey'], m.Order.paid_at != None).all():
            if order.has_skin_in_the_game_badge():
                has_skin_in_the_game = True
                break
        if not has_skin_in_the_game:
            site_admin_nostr_public_key = get_site_admin_config()['nostr_private_key'].public_key.hex()
            site_admin = m.User.query.filter_by(nostr_public_key=site_admin_nostr_public_key).first()
            if not site_admin:
                return jsonify({'message': "Site not configured!"}), 500
            badge_listing = m.Listing.query.join(m.Item).filter((m.Listing.key == app.config['BADGE_DEFINITION_SKIN_IN_THE_GAME']['badge_id']) & (m.Item.seller_id == site_admin.id)).first()
            if not badge_listing:
                return jsonify({'message': "Site not configured!"}), 500
            message = f"User needs Skin in the Game in order to bid."
            birdwatcher.publish_bid_status(auction, request.json['id'], 'pending', message, badge_stall_id=site_admin.stall_id, badge_product_id=str(badge_listing.uuid))
            is_settled = False

    bid = m.Bid(nostr_event_id=request.json['id'], auction=auction, buyer_nostr_public_key=request.json['pubkey'], amount=amount)
    if is_settled:
        bid.settled_at = datetime.utcnow()
    db.session.add(bid)

    app.logger.info(f"New bid for merchant {merchant_pubkey} auction {auction_event_id}: {request.json['content']}!")

    duration_extended = auction.extend()

    if is_settled:
        birdwatcher.publish_bid_status(auction, request.json['id'], 'accepted', duration_extended=duration_extended)
        if top_bid:
            birdwatcher.send_dm(merchant.parse_merchant_private_key(), top_bid.buyer_nostr_public_key,
                                f"You have been outbid on the auction: {auction.item.title}!")

    db.session.commit()

    return jsonify({})
