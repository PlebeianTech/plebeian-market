import btc2fiat
from datetime import datetime, timedelta
from io import BytesIO
import os
import secrets
import bleach
import ecdsa
from ecdsa.keys import BadSignatureError
from flask import Blueprint, jsonify, request
import jwt
import lnurl
from pycoin.symbols.btc import network as BTC
import pyqrcode
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import func

from extensions import db
import models as m
from main import app, get_btc_client, get_lnd_client, get_s3, get_twitter
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

    token = jwt.encode({'user_key': user.key, 'exp': datetime.utcnow() + timedelta(days=30)}, app.config['SECRET_KEY'], "HS256")

    return jsonify({'success': True, 'token': token, 'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/users/<string:nym>', methods=['GET'])
def profile(nym):
    requesting_user = get_user_from_token(get_token_from_request())
    for_user_id = requesting_user.id if requesting_user else None
    if request.method == 'GET':
        user = m.User.query.filter_by(nym=nym).first()
        if not user:
            return jsonify({'message': "User not found"}), 404
        return jsonify({'user': user.to_dict(for_user=for_user_id)})

@api_blueprint.route('/api/users/me', methods=['GET', 'PUT'])
@user_required
def me(user):
    if request.method == 'GET':
        return jsonify({'user': user.to_dict(for_user=user.id)})
    else:
        if 'nym' in request.json:
            clean_nym = (request.json['nym'] or "").lower().strip()
            if len(clean_nym) < 3:
                return jsonify({'message': "Your nym needs to be at least 3 characters long!"}), 400
            if not clean_nym.isalnum():
                return jsonify({'message': "Your nym can only contain letters and numbers!"}), 400
            user.nym = clean_nym
        if 'twitter_username' in request.json:
            clean_username = (request.json['twitter_username'] or "").lower().strip()
            if clean_username.startswith("@"):
                clean_username = clean_username.removeprefix("@")
            if not clean_username:
                return jsonify({'message': "Invalid Twitter username!"}), 400
            if clean_username != user.twitter_username:
                if user.nym == user.twitter_username:
                    # NB: if the user has set a custom nym, don't overwrite that!
                    user.nym = clean_username
                user.twitter_username = clean_username

                twitter = get_twitter()

                twitter_user = twitter.get_user(user.twitter_username)

                if not twitter_user:
                    return jsonify({'message': "Twitter profile not found!"}), 400

                if app.config['ENV'] == 'prod':
                    if user.twitter_username not in app.config['TWITTER_USER_MIN_AGE_DAYS_WHITELIST']:
                        if twitter_user['created_at'] > (datetime.utcnow() - timedelta(days=app.config['TWITTER_USER_MIN_AGE_DAYS'])):
                            return jsonify({'message': f"Twitter profile needs to be at least {app.config['TWITTER_USER_MIN_AGE_DAYS']} days old!"}), 400

                if not user.fetch_twitter_profile_image(twitter_user['profile_image_url'], get_s3()):
                    return jsonify({'message': "Error fetching profile picture!"}), 400

                if not user.fetch_twitter_profile_banner(twitter_user['profile_banner_url'], get_s3()):
                    return jsonify({'message': "Error fetching profile banner!"}), 400

                user.twitter_username_verified = False

                plebeian_twitter_user = twitter.get_user(app.config['TWITTER_USER'])

                user.twitter_username_verification_tweet_id = plebeian_twitter_user['pinned_tweet_id']

        if 'contribution_percent' in request.json:
            user.contribution_percent = request.json['contribution_percent']

        if 'xpub' in request.json:
            k = BTC.parse(request.json['xpub'])
            if not k:
                return jsonify({'message': "Invalid XPUB."}), 400
            try:
                first_address = k.subkey(0).subkey(0).address()
            except AttributeError:
                return jsonify({'message': "Invalid XPUB."}), 400
            user.xpub = request.json['xpub']
            user.xpub_index = 0

        if 'stall_name' in request.json:
            user.stall_name = bleach.clean(request.json['stall_name'])

        if 'stall_description' in request.json:
            user.stall_description = bleach.clean(request.json['stall_description'])

        try:
            db.session.commit()
        except IntegrityError:
            return jsonify({'message': "Somebody already registered this Twitter username!"}), 400

        return jsonify({'user': user.to_dict(for_user=user.id)})

@api_blueprint.route('/api/users/me/verify-twitter', methods=['PUT'])
@user_required
def verify_twitter(user):
    liking_usernames = get_twitter().get_tweet_likes(user.twitter_username_verification_tweet_id)
    if not user.twitter_username.lower() in liking_usernames:
        return jsonify({'message': "Please like the tweet to verify your username."}), 400
    else:
        user.twitter_username_verified = True
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
def messages(user):
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
    sales = m.Sale.query.filter(m.Item.id == m.Sale.item_id, m.Item.seller_id == user.id).all()

    return jsonify({'sales': [s.to_dict() for s in sales]})

@api_blueprint.route("/api/auctions", defaults={'cls': m.Auction, 'singular': 'auction'},
    methods=['POST'])
@api_blueprint.route("/api/listings", defaults={'cls': m.Listing, 'singular': 'listing'},
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

    existing_count = db.session.query(func.count(cls.id).label('count')).first().count
    entity = cls(item=item, key=cls.generate_key(existing_count), **validated_entity)
    if isinstance(entity, m.Auction):
        entity.seller=user # TODO: remove this after removing the field from Auction
    db.session.add(entity)
    db.session.commit()

    if isinstance(entity, m.Auction):
        # follow your own auctions!
        user_auction = m.UserAuction(user_id=user.id, auction_id=entity.id, following=True)
        db.session.add(user_auction)
        db.session.commit()

    return jsonify({singular: entity.to_dict(for_user=user.id)})

@api_blueprint.route('/api/campaigns', methods=['GET', 'POST'])
@user_required
def campaigns(user):
    if request.method == 'GET':
        campaigns = [c.to_dict(for_user=user.id) for c in user.campaigns]
        return jsonify({'campaigns': campaigns})
    else:
        for k in ['title', 'description']:
            if k not in request.json:
                return jsonify({'message': f"Missing key: {k}."}), 400

        try:
            validated = m.Campaign.validate_dict(request.json)
        except m.ValidationError as e:
            return jsonify({'message': e.message}), 400

        campaign_count = db.session.query(func.count(m.Campaign.id).label('count')).first().count
        key = m.Campaign.generate_key(campaign_count)
        campaign = m.Campaign(owner=user, key=key, **validated)
        db.session.add(campaign)
        db.session.commit()

        return jsonify({'campaign': campaign.to_dict(for_user=user.id)})

@api_blueprint.route('/api/auctions/featured',
    defaults={'cls': m.Auction, 'plural': 'auctions'},
    methods=['GET'])
@api_blueprint.route('/api/listings/featured',
    defaults={'cls': m.Listing, 'plural': 'listings'},
    methods=['GET'])
def featured(cls, plural):
    entities = cls.query.filter((cls.start_date != None) & (cls.start_date <= datetime.utcnow()))
    entities = entities.filter((cls.item_id == m.Item.id) & ~m.Item.is_hidden)
    if cls == m.Auction:
        entities = entities.filter((cls.end_date == None) | (cls.end_date > datetime.utcnow()))
    elif cls == m.Listing:
        entities = entities.filter(cls.available_quantity != 0)
    return jsonify({plural: [e.to_dict() for e in sorted(entities.all(), key=cls.featured_sort_key, reverse=True)]})

@api_blueprint.route('/api/auctions/<string:key>',
    defaults={'cls': m.Auction, 'singular': 'auction'},
    methods=['GET', 'PUT', 'DELETE'])
@api_blueprint.route('/api/listings/<string:key>',
    defaults={'cls': m.Listing, 'singular': 'listing'},
    methods=['GET', 'PUT', 'DELETE'])
def get_put_delete_entity(key, cls, singular):
    user = get_user_from_token(get_token_from_request())
    entity = cls.query.filter_by(key=key).first()
    if not entity:
        return jsonify({'message': "Not found."}), 404

    if request.method == 'GET':
        if isinstance(entity, m.Auction):
            entity.set_contribution()
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

        ########
        # NB: temporary measure to generate items for existing auctions
        if isinstance(entity, m.Auction):
            entity.ensure_item()
        ########

        if user.id != entity.item.seller_id and not is_changing_hidden_state:
            return jsonify({'message': "Unauthorized"}), 401

        if isinstance(entity, m.Auction) and entity.started and not is_changing_hidden_state_only:
            return jsonify({'message': "Cannot edit auctions once started."}), 403

        if request.method == 'PUT':
            try:
                validated_item = m.Item.validate_dict(request.json)
                validated = cls.validate_dict(request.json)
            except m.ValidationError as e:
                return jsonify({'message': e.message}), 400

            for k, v in validated_item.items():
                setattr(entity.item, k, v)
            for k, v in validated.items():
                setattr(entity, k, v)

            db.session.commit()

            return jsonify({})
        elif request.method == 'DELETE':
            for sale in entity.sales:
                if isinstance(entity, m.Auction):
                    sale.auction = None
                elif isinstance(entity, m.Listing):
                    sale.listing = None
            db.session.delete(entity)
            db.session.commit()

            return jsonify({})

@api_blueprint.route('/api/campaigns/<string:key>', methods=['GET', 'PUT', 'DELETE'])
def campaign(key):
    user = get_user_from_token(get_token_from_request())
    campaign = m.Campaign.query.filter_by(key=key).first()
    if not campaign:
        return jsonify({'message': "Not found."}), 404

    if request.method == 'GET':
        return jsonify({'campaign': campaign.to_dict(for_user=(user.id if user else None))})
    else:
        if not user:
            return jsonify({'message': "Unauthorized"}), 401
        if user.id != campaign.owner_id:
            return jsonify({'message': "Unauthorized"}), 401

        if campaign.started:
            return jsonify({'message': "Cannot edit a campaign after it started."}), 403

        if request.method == 'PUT':
            try:
                validated = m.Campaign.validate_dict(request.json)
            except m.ValidationError as e:
                return jsonify({'message': e.message}), 400

            for k, v in validated.items():
                setattr(campaign, k, v)

            db.session.commit()

            return jsonify({})
        elif request.method == 'DELETE':
            db.session.delete(campaign)
            db.session.commit()

            return jsonify({})

@api_blueprint.route('/api/campaigns/<string:key>/start', methods=['PUT'])
@user_required
def start_campaign(user, key):
    campaign = m.Campaign.query.filter_by(key=key).first()
    if not campaign:
        return jsonify({'message': "Not found."}), 404
    if campaign.owner_id != user.id:
        return jsonify({'message': "Unauthorized"}), 401
    if campaign.started:
        return jsonify({'message': "Campaign already started!"}), 403

    campaign.start_date = datetime.utcnow()
    db.session.commit()
    return jsonify({})

@api_blueprint.route('/api/campaigns/<string:key>/end', methods=['PUT'])
@user_required
def end_campaign(user, key):
    campaign = m.Campaign.query.filter_by(key=key).first()
    if not campaign:
        return jsonify({'message': "Not found."}), 404
    if campaign.owner_id != user.id:
        return jsonify({'message': "Unauthorized"}), 401
    if campaign.ended:
        return jsonify({'message': "Campaign already ended!"}), 403

    campaign.end_date = datetime.utcnow()
    db.session.commit()
    return jsonify({})

@api_blueprint.route('/api/auctions/<string:key>/follow', methods=['PUT'])
@user_required
def follow_auction(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404

    follow = bool(request.json['follow'])

    if auction.seller_id == user.id and not follow:
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

@api_blueprint.route('/api/auctions/<string:key>/start-twitter',
    defaults={'cls': m.Auction, 'singular': 'auction', 'plural': 'auctions'},
    methods=['PUT'])
@api_blueprint.route('/api/listings/<string:key>/start-twitter',
    defaults={'cls': m.Listing, 'singular': 'listing', 'plural': 'listings'},
    methods=['PUT'])
@user_required
def start(user, key, cls, singular, plural):
    entity = cls.query.filter_by(key=key).first()
    if not entity:
        return jsonify({'message': "Not found."}), 404

    ########
    # NB: temporary measure to generate items for existing auctions
    if isinstance(entity, m.Auction):
        entity.ensure_item()
    ########

    if entity.item.seller_id != user.id:
        return jsonify({'message': "Unauthorized"}), 401

    if user.contribution_percent is None:
        return jsonify({'message': "User did not set a contribution."}), 400
    if isinstance(entity, m.Listing):
        if not user.xpub:
            return jsonify({'message': "User did not set an XPUB."}), 400

    twitter = get_twitter()
    twitter_user = twitter.get_user(user.twitter_username)
    if not twitter_user:
        return jsonify({'message': "Twitter profile not found!"}), 400

    if not user.fetch_twitter_profile_image(twitter_user['profile_image_url'], get_s3()):
        return jsonify({'message': "Error fetching profile picture!"}), 500

    if not user.fetch_twitter_profile_banner(twitter_user['profile_banner_url'], get_s3()):
        return jsonify({'message': "Error fetching profile banner!"}), 500

    tweets = twitter.get_sale_tweets(twitter_user['id'], plural)
    tweet = None
    for t in sorted(tweets, key=lambda t: t['created_at'], reverse=True):
        # we basically pick the last tweet that matches the auction
        if t['auction_key'] == entity.key:
            tweet = t
            break

    if not tweet:
        return jsonify({'message': "Tweet not found."}), 400

    if not tweet['photos']:
        return jsonify({'message': "Tweet does not have any attached pictures."}), 400

    user.twitter_username_verified = True
    entity.twitter_id = tweet['id']
    entity.start_date = datetime.utcnow()

    if isinstance(entity, m.Auction):
        entity.end_date = entity.start_date + timedelta(hours=entity.duration_hours)

    m.Media.query.filter_by(item_id=entity.item.id).delete()
    ########
    # TODO: remove this after removing auction_id from Media
    auction_id = None
    if isinstance(entity, m.Auction):
        m.Media.query.filter_by(auction_id=entity.id).delete()
        auction_id = entity.id
    ########

    s3 = get_s3()
    for i, photo in enumerate(tweet['photos'], 1):
        media = m.Media(item_id=entity.item.id, auction_id=auction_id, twitter_media_key=photo['media_key'], url=photo['url'])
        if not media.fetch(s3, f"{singular}_{entity.key}_media_{i}"):
            return jsonify({'message': "Error fetching picture!"}), 400
        db.session.add(media)

    db.session.commit()

    return jsonify({})

@api_blueprint.route('/api/auctions/<string:key>/bids', methods=['POST'])
@user_required
def post_bid(user, key):
    auction = m.Auction.query.filter_by(key=key).first()
    if not auction:
        return jsonify({'message': "Not found."}), 404

    if not auction.started or auction.ended:
        return jsonify({'message': "Auction not running."}), 403

    amount = int(request.json['amount'])

    top_bid = auction.get_top_bid()
    if top_bid and amount <= top_bid.amount:
        return jsonify({'message': f"The top bid is currently {top_bid.amount}. Your bid needs to be higher!"}), 400
    elif amount <= auction.starting_bid:
        return jsonify({'message': f"Your bid needs to be higher than {auction.starting_bid}, the starting bid."}), 400

    response = get_lnd_client().add_invoice(value=app.config['LND_BID_INVOICE_AMOUNT'], expiry=app.config['LND_BID_INVOICE_EXPIRY'])

    payment_request = response.payment_request

    bid = m.Bid(auction=auction, buyer=user, amount=amount, payment_request=payment_request)
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

    qr = BytesIO()
    pyqrcode.create(payment_request).svg(qr, omithw=True, scale=4)

    return jsonify({
        'payment_request': payment_request,
        'qr': qr.getvalue().decode('utf-8'),
        'messages': [
            "Your bid will be confirmed once you scan the QR code.",
        ] + (["Started following the auction."] if started_following else []),
    })

@api_blueprint.route('/api/listings/<string:key>/buy', methods=['PUT'])
@user_required
def put_buy(user, key):
    listing = m.Listing.query.filter_by(key=key).first()
    if not listing:
        return jsonify({'message': "Not found."}), 404
    if not listing.started or listing.ended:
        return jsonify({'message': "Listing not active."}), 403

    # NB: for now the quantity is always 1,
    # but storing this in the DB makes it easy in case we want to change this later on:
    # it would just be a matter of getting a quantity from the UI and sending it here to be used instead of 1.
    quantity = 1

    if listing.available_quantity < quantity:
        return jsonify({'message': "Not enough items in stock!"}), 400

    btc2usd = btc2fiat.get_value('kraken')

    price_sats = int(listing.price_usd / btc2usd * app.config['SATS_IN_BTC'])
    shipping_domestic_sats = int(listing.item.shipping_domestic_usd / btc2usd * app.config['SATS_IN_BTC'])
    shipping_worldwide_sats = int(listing.item.shipping_worldwide_usd / btc2usd * app.config['SATS_IN_BTC'])

    contribution_amount = int(listing.item.seller.contribution_percent / 100 * price_sats * quantity)
    response = get_lnd_client().add_invoice(value=contribution_amount, expiry=app.config['LND_BID_INVOICE_EXPIRY'])
    contribution_payment_request = response.payment_request

    amount = (price_sats * quantity) - contribution_amount

    k = BTC.parse(listing.item.seller.xpub)

    btc = get_btc_client()

    address = None
    while True:
        if listing.item.seller.xpub_index is None:
            listing.item.seller.xpub_index = 0

        address = k.subkey(0).subkey(listing.item.seller.xpub_index).address()

        listing.item.seller.xpub_index += 1

        existing_txs = btc.get_funding_txs(address)
        if existing_txs is None:
            return jsonify({'message': "Error reading from mempool API!"}), 500

        if existing_txs:
            app.logger.warning("Skipping address with existing txs.")
            continue

        if m.Sale.query.filter_by(address=address).first():
            app.logger.warning("Skipping address with existing sale.")
            continue

        sale = m.Sale(item_id=listing.item.id, listing_id=listing.id, buyer_id=user.id,
            address=address,
            price_usd=listing.price_usd,
            price=price_sats, shipping_domestic=shipping_domestic_sats, shipping_worldwide=shipping_worldwide_sats,
            quantity=quantity,
            amount=amount,
            contribution_amount=contribution_amount, contribution_payment_request=contribution_payment_request)
        db.session.add(sale)

        try:
            db.session.commit()
        except IntegrityError:
            return jsonify({'message': "Address already in use. Please try again."}), 500

        break

    return jsonify({'sale': sale.to_dict()})

@api_blueprint.route("/api/users/<nym>/auctions",
    defaults={'plural': 'auctions'},
    methods=['GET'])
@api_blueprint.route("/api/users/<nym>/listings",
    defaults={'plural': 'listings'},
    methods=['GET'])
def get_user_entities(nym, plural):
    for_user = get_user_from_token(get_token_from_request())
    for_user_id = for_user.id if for_user else None

    user = m.User.query.filter_by(nym=nym).first()

    if not user:
        return jsonify({'message': "User not found."}), 404

    entities = {}
    for item in user.items:
        for entity in getattr(item, plural):
            if entity.matches_filter(for_user_id, request.args.get('filter')):
                entities[f"{plural}_{entity.id}"] = entity

    # TODO: this part can be removed after we ensure all auctions in the DB have corresponding items
    # (and at that point, FilterStateMixin becomes useless as well)
    ########
    if plural == 'auctions':
        for auction in user.auctions:
            if f"auctions_{auction.id}" not in entities:
                if auction.matches_filter(for_user_id, request.args.get('filter')):
                    entities[f"auctions_{auction.id}"] = auction
    ########

    sorted_entities = sorted(entities.values(), key=lambda l: l.created_at, reverse=True)

    return jsonify({plural: [e.to_dict(for_user=for_user_id) for e in sorted_entities]})
