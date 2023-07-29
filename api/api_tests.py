import base64
import btc2fiat
from datetime import datetime, timedelta
import dateutil.parser
import ecdsa
import json
from nostr.event import Event, EncryptedDirectMessage
from nostr.key import PrivateKey
import requests
import time
import unittest

from main import app
from utils import hash_create, usd2sats

# just a one-pixel PNG used for testing
ONE_PIXEL_PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIW2P4v5ThPwAG7wKklwQ/bwAAAABJRU5ErkJggg==")

# XPUBs to use for tests and some addresses belonging to them
XPUB = "xpub6CUGRUonZSQ4TWtTMmzXdrXDtypWKiKrhko4egpiMZbpiaQL2jkwSB1icqYh2cfDfVxdx4df189oLKnC5fSwqPfgyP3hooxujYzAu3fDVmz"
ADDRESSES = ["bc1qjh4xdrsry27enkk9fl7ujzyadrjkcw4p2uy76c", "bc1qzt9cgxvxqvl4ajdy5xatuwj8xwd74jquwequst", "bc1q0afc6ehrw3vxd9ylrwvvwtqqvw83d3aqsyyxxp", "bc1qxe8ng3f7wg40ym6lscd2lwm3q5tkah8wyh2cmz", "bc1q7jd276fwrt98m80zw02m25u266t8036d9mpv3u", "bc1q8nht6h0jtaeek5p96c06f03rgmad49la4u7epm", "bc1qjxletyx4euzp94dnlmqjsnt3vjckr3jsu278v3"]
# an XPUB to test campaigns, different from the other one
OTHER_XPUB = "xpub6D93ecgDqmNjxsM6hN7Qf5Wxt8y5Zv4VmumbMe7xXcmBmE5ti3BRSZfkwrf7nawmzKcgRas978URPQkwBdoBWvsNLPyepEWcCc2kKh2Kk2x"
OTHER_XPUB_ADDRESSES = ["bc1qeauv7festyh2d85ugskzlqucnp594es3t3dhe7", "bc1qenglrz38j2amql5twlt7npaq495hl5n8rqujke", "bc1q3edvv3grv3l0pskxncu9sslv0rv2rlwmlwn6e4"]

# some random nostr keys
NOSTR_PRIVATE_KEY_1 = PrivateKey()
NOSTR_KEY_1 = NOSTR_PRIVATE_KEY_1.public_key.hex()
NOSTR_PRIVATE_KEY_2 = PrivateKey()
NOSTR_KEY_2 = NOSTR_PRIVATE_KEY_2.public_key.hex()
NOSTR_BUYER_PRIVATE_KEY = PrivateKey()

ONE_DOLLAR_SATS = usd2sats(1, btc2fiat.get_value('kraken'))

BID_NOSTR_EVENT_KIND = 1021

class TestApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.returned_k1s = set()
        self.returned_tokens = set()
        super(TestApi, self).__init__(*args, **kwargs)

    def do(self, f, path, params=None, json=None, headers=None, files=None):
        if files is None:
            files = {}
        API_BASE_URL = app.config['API_BASE_URL']
        response = f(f"{API_BASE_URL}{path}", params=params, json=json, headers=headers, files=files)
        return response.status_code, response.json() if response.status_code in (200, 400, 401, 402, 403, 404) else None

    def get(self, path, params=None, headers=None):
        return self.do(requests.get, path, params=params, headers=headers)

    def post(self, path, json, headers=None, files=None):
        return self.do(requests.post, path, json=json, headers=headers, files=files)

    def put(self, path, json, headers=None, files=None):
        return self.do(requests.put, path, json=json, headers=headers, files=files)

    def delete(self, path, headers=None):
        return self.do(requests.delete, path, headers=headers)

    def get_auth_headers(self, token):
        return {'X-Access-Token': token}

    def update_user(self, token, expect_success=True, **kwargs):
        code, response = self.put("/api/users/me", kwargs,
            headers=self.get_auth_headers(token))
        if expect_success:
            self.assertEqual(code, 200)
        return code, response

    def generate_lnauth_key(self):
        return ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

    def lnurl_auth(self, key, expect_success=True, **kwargs):
        code, response = self.get(f"/api/login/lnurl")
        self.assertEqual(code, 200)
        self.assertIn('k1', response)
        self.assertIn('svg', response['qr'])

        k1 = response['k1']

        self.assertNotIn(k1, self.returned_k1s)
        self.returned_k1s.add(k1)

        # not logged in yet...
        code, response = self.get(f"/api/login/lnurl", {'k1': k1})
        self.assertEqual(code, 200)
        self.assertFalse(response['success'])

        sig = key.sign_digest(bytes.fromhex(k1), sigencode=ecdsa.util.sigencode_der)

        # try sending another k1 (but properly signed)...
        another_k1 = list(bytes.fromhex(k1))
        another_k1[0] = (another_k1[0] + 1) % 255
        another_k1 = bytes(another_k1)
        another_sig = key.sign_digest(another_k1, sigencode=ecdsa.util.sigencode_der)
        code, response = self.get(f"/api/login/lnurl",
            {'k1': another_k1.hex(),
             'key': key.verifying_key.to_string().hex(),
             'sig': another_sig.hex()})
        self.assertEqual(code, 400)
        self.assertIn("verification failed", response['message'].lower())

        # try sending a wrong signature
        code, response = self.get(f"/api/login/lnurl",
            {'k1': k1,
             'key': key.verifying_key.to_string().hex(),
             'sig': another_sig.hex()})
        self.assertEqual(code, 400)
        self.assertIn("verification failed", response['message'].lower())

        # send the correct signature
        code, response = self.get(f"/api/login/lnurl",
            {'k1': k1,
             'key': key.verifying_key.to_string().hex(),
             'sig': sig.hex()})
        self.assertEqual(code, 200)
        self.assertNotIn('token', response)

        # get the token
        code, response = self.get(f"/api/login/lnurl",
            {'k1': k1})

        if expect_success:
            self.assertEqual(code, 200)
            self.assertIn('token', response)

            token = response['token']

            self.assertNotIn(token, self.returned_tokens)
            self.returned_tokens.add(token)

            # can't request the token again if we already got it once
            code, response = self.get(f"/api/login/lnurl",
                {'k1': k1,
                'key': key.verifying_key.to_string().hex(),
                'sig': sig.hex()})
            self.assertEqual(code, 400)

            if kwargs:
                self.update_user(token, **kwargs)

            return token
        else:
            self.assertNotEqual(code, 200)

    def nostr_auth(self, private_key, expect_success=True, **kwargs):
        # try with another content...
        auth_event = Event(kind=1, content="chairman auth", public_key=private_key.public_key.hex())
        private_key.sign_event(auth_event)
        signed_event_json = json.loads(auth_event.to_message())[1]
        code, response = self.put(f"/api/login/nostr", signed_event_json)
        self.assertEqual(code, 400)
        self.assertIn("invalid", response['message'].lower())

        # try the correct content but a wrong signature
        auth_event = Event(kind=1, content="Plebeian Market Login", public_key=private_key.public_key.hex())
        private_key.sign_event(auth_event)
        signed_event_json = json.loads(auth_event.to_message())[1]
        signed_event_json['sig'] = "1234"
        code, response = self.put(f"/api/login/nostr", signed_event_json)
        self.assertEqual(code, 400)
        self.assertIn("invalid", response['message'].lower())

        # now finally do it
        auth_event = Event(kind=1, content="Plebeian Market Login", public_key=private_key.public_key.hex())
        private_key.sign_event(auth_event)
        signed_event_json = json.loads(auth_event.to_message())[1]
        code, response = self.put(f"/api/login/nostr", signed_event_json)

        if expect_success:
            self.assertEqual(code, 200)
            self.assertIn('token', response)

            token = response['token']

            self.assertNotIn(token, self.returned_tokens)
            self.returned_tokens.add(token)

            if kwargs:
                self.update_user(token, **kwargs)

            return token
        else:
            self.assertNotEqual(code, 200)

    def test_listings(self):
        token_1 = self.nostr_auth(PrivateKey(), twitter_username='fixie')
        token_2 = self.nostr_auth(PrivateKey(), twitter_username='fixie_buyer')

        # GET listings to see there are none there
        code, response = self.get("/api/users/fixie/listings",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['listings']), 0)

        # can't create a listing without price
        code, response = self.post("/api/users/me/listings",
            {'title': "My 1st fixie",
             'description': "Selling something cool for a fixed price",
             'available_quantity': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertIn("missing", response['message'].lower())
        self.assertIn("price", response['message'].lower())

        # finally create a listing
        code, response = self.post("/api/users/me/listings",
            {'title': "My 1st fixie",
             'description': "Selling something cool for a fixed price",
             'shipping_domestic_usd': 5,
             'shipping_worldwide_usd': 10,
             'price_usd': 10,
             'available_quantity': 5},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertIn('listing', response)

        listing_key = response['listing']['key']
        listing_uuid = response['listing']['uuid']

        # GET listings to see our new listing
        code, response = self.get("/api/users/fixie/listings?filter=new",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['listings']), 1)
        self.assertEqual(response['listings'][0]['key'], listing_key)
        self.assertEqual(response['listings'][0]['available_quantity'], 5)

        code, response = self.get(f"/api/listings/{listing_key}")
        self.assertEqual(code, 200)
        listing_merchant_public_key = response['listing']['merchant_public_key']
        self.assertIsNotNone(listing_merchant_public_key)
        self.assertIsNone(response['listing']['nostr_event_id'])

        purchase_event_json = {
            'type': 0,
            'id': hash_create(4),
            'name': "JOHN APPLESEEDPHRASE",
            'address': "7 Záhony u. Budapest, 1031 Hungary",
            'message': "Please deliver to this point: 47.5607, 19.0544",
            'contact': {'email': "test@plebeian.market"},
            'items': [{'product_id': listing_uuid, 'quantity': 2}],
            'shipping_id': 'WORLD',
        }
        purchase_event = EncryptedDirectMessage(recipient_pubkey=listing_merchant_public_key, cleartext_content=json.dumps(purchase_event_json))
        NOSTR_BUYER_PRIVATE_KEY.sign_event(purchase_event)
        signed_event_json = json.loads(purchase_event.to_message())[1]

        copy_of_signed_event_json = dict(signed_event_json)
        copy_of_signed_event_json['sig'] = "12345"
        code, response = self.post(f"/api/merchants/{listing_merchant_public_key}/messages", copy_of_signed_event_json)
        self.assertEqual(code, 400)
        self.assertIn("invalid event signature", response['message'].lower())

        copy_of_signed_event_json = dict(signed_event_json)
        copy_of_signed_event_json['kind'] = 1 # trying to change the event kind after it was signed...
        code, response = self.post(f"/api/merchants/{listing_merchant_public_key}/messages", copy_of_signed_event_json)
        self.assertEqual(code, 400)
        self.assertIn("invalid event id", response['message'].lower())

        # can't publish the listing before setting the XPUB
        code, response = self.put(f"/api/listings/{listing_key}/publish", {},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertIn("wallet", response['message'].lower())

        # set the xpub
        _, response = self.update_user(token_1, wallet=XPUB)
        self.assertEqual(response['user']['wallet_index'], 0)

        # can't buy because the listing has not been published yet
        code, response = self.post(f"/api/merchants/{listing_merchant_public_key}/messages", signed_event_json)
        self.assertEqual(code, 403)
        self.assertIn("not active", response['message'].lower())

        # start the listing
        code, response = self.put(f"/api/listings/{listing_key}/publish", {},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # the listing now has a Nostr event ID
        code, response = self.get(f"/api/listings/{listing_key}")
        self.assertEqual(code, 200)
        listing_initial_nostr_event_id = response['listing']['nostr_event_id']
        self.assertIsNotNone(listing_initial_nostr_event_id)

        # other users cannot add images
        code, response = self.post(f"/api/listings/{listing_key}/media",
            headers=self.get_auth_headers(token_2), json={},
            files={'media': ('one_pixel.png', ONE_PIXEL_PNG)})
        self.assertEqual(code, 401)
        code, response = self.get(f"/api/listings/{listing_key}")
        self.assertEqual(len(response['listing']['media']), 0)

        # the owner however, can!
        code, response = self.post(f"/api/listings/{listing_key}/media",
            headers=self.get_auth_headers(token_1), json={},
            files={'media': ('one_pixel.png', ONE_PIXEL_PNG)})
        self.assertEqual(code, 200)
        self.assertTrue(response['media'][0]['url'].endswith('.png'))
        self.assertEqual(response['media'][0]['index'], 1)
        media_hash = response['media'][0]['hash']

        code, response = self.get(f"/api/listings/{listing_key}")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['listing']['media']), 1)
        self.assertIn(media_hash, [m['hash'] for m in response['listing']['media']])
        listing_after_media_added_nostr_event_id = response['listing']['nostr_event_id']
        self.assertNotEqual(listing_after_media_added_nostr_event_id, listing_initial_nostr_event_id)

        # other users cannot delete images...
        code, response = self.delete(f"/api/listings/{listing_key}/media/{media_hash}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 401)
        code, response = self.get(f"/api/listings/{listing_key}")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['listing']['media']), 1)

        # CAN EDIT the listing even after published
        code, response = self.put(f"/api/listings/{listing_key}",
            {'available_quantity': 10, 'media': [{'hash': media_hash, 'index': 500}]},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # the Nostr event ID changed again!
        code, response = self.get(f"/api/listings/{listing_key}")
        self.assertEqual(code, 200)
        listing_after_edit_nostr_event_id = response['listing']['nostr_event_id']
        self.assertNotEqual(listing_after_edit_nostr_event_id, listing_after_media_added_nostr_event_id)
        self.assertNotEqual(listing_after_edit_nostr_event_id, listing_initial_nostr_event_id)

        # anyone looking at our listing will see the changes
        code, response = self.get("/api/users/fixie/listings")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['listings']), 1)
        self.assertEqual(response['listings'][0]['key'], listing_key)
        self.assertEqual(response['listings'][0]['available_quantity'], 10)
        self.assertEqual([m for m in response['listings'][0]['media'] if m['hash'] == media_hash][0]['index'], 500)

        # the owner CAN delete images!
        code, response = self.delete(f"/api/listings/{listing_key}/media/{media_hash}",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # and we are back to 0 now!
        code, response = self.get(f"/api/listings/{listing_key}")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['listing']['media']), 0)
        self.assertNotIn(media_hash, [m['hash'] for m in response['listing']['media']])
        listing_after_media_deleted_nostr_event_id = response['listing']['nostr_event_id']
        self.assertNotEqual(listing_after_media_deleted_nostr_event_id, listing_after_media_added_nostr_event_id)
        self.assertNotEqual(listing_after_media_deleted_nostr_event_id, listing_after_edit_nostr_event_id)
        self.assertNotEqual(listing_after_media_deleted_nostr_event_id, listing_initial_nostr_event_id)

        # the seller has no orders
        code, response = self.get("/api/users/me/orders", {},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['orders']), 0)

        # try to buy the product again
        code, response = self.post(f"/api/merchants/{listing_merchant_public_key}/messages", signed_event_json)
        self.assertEqual(code, 200)

        # the order is there!
        code, response = self.get("/api/users/me/orders", {},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['orders']), 1)
        self.assertEqual(response['orders'][0]['uuid'], purchase_event_json['id'])
        self.assertEqual(response['orders'][0]['buyer']['name'], purchase_event_json['name'])

        code, response = self.get("/api/users/me", headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertTrue(response['user']['wallet_index'] > 0)

        time.sleep(5)

        # now the available quantity is two less
        code, response = self.get(f"/api/listings/{listing_key}", {},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertEqual(response['listing']['available_quantity'], 8)

        # can simply DELETE the listing while active!
        code, response = self.delete(f"/api/listings/{listing_key}",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # and... GONE it is
        code, response = self.get(f"/api/listings/{listing_key}", {},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 404)

    def test_000_user(self):
        key_1 = PrivateKey()

        token_1 = self.nostr_auth(key_1)

        code, response = self.get("/api/users/me", headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        identity_1 = response['user']['identity']

        # set user details
        self.update_user(token_1, twitter_username='username1', contribution_percent=1)

        # check user details again
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['contribution_percent'], 1)
        self.assertEqual(response['user']['has_items'], False)
        self.assertEqual(response['user']['has_own_items'], False)

        # set an email address
        code, response = self.update_user(token_1, False, email="brokenemail")
        self.assertEqual(code, 400)
        self.assertIn("not valid", response['message'])

        code, response = self.update_user(token_1, False, email="brokenemail@plebinexistingdomain.com")
        self.assertEqual(code, 400)
        self.assertIn("not valid", response['message']) # inexisting domain

        _, response = self.update_user(token_1, email="goodemail@plebeian.market")
        self.assertEqual(response['user']['email'], "goodemail@plebeian.market")
        self.assertFalse(response['user']['email_verified']) # we don't even support email verification yet!

        # try to verify the Twitter username
        code, response = self.put("/api/users/me/verify/twitter",
            {'phrase': "i hate you"},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)

        # check user details (again)
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['twitter_username'], 'username1')
        self.assertFalse(response['user']['twitter_username_verified'])

        # verify Twitter for good now
        code, response = self.put("/api/users/me/verify/twitter",
            {'phrase': "i am ME"},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # check user details (yet again)
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['twitter_username'], 'username1')
        self.assertTrue(response['user']['twitter_username_verified'])

        # can log in again with the same key
        self.nostr_auth(key_1, expect_success=True)
        """
        # link Nostr account to this user
        code, response = self.update_user(token_1, nostr_public_key=NOSTR_KEY_1)
        self.assertEqual(code, 200)

        # key has been set, but not yet verified
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['nostr_public_key'], NOSTR_KEY_1)
        self.assertFalse(response['user']['nostr_public_key_verified'])

        # try to verify the Nostr key
        code, response = self.put("/api/users/me/verify/nostr",
            {'phrase': "i am somebody else"},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)

        # it hasn't been verified...
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['nostr_public_key'], NOSTR_KEY_1)
        self.assertFalse(response['user']['nostr_public_key_verified'])

        # can't log in with that Nostr account!
        self.nostr_auth(NOSTR_PRIVATE_KEY_1, expect_success=False)

        # verify the Nostr key for real this time
        code, response = self.put("/api/users/me/verify/nostr",
            {'phrase': "I AM ME"},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # now we can log in with nostr
        token_1_1 = self.nostr_auth(NOSTR_PRIVATE_KEY_1, expect_success=True)

        # check user details - it should be the same user as when we authenticated with lnurl!
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['identity'], identity_1)
        self.assertEqual(response['user']['twitter_username'], 'username1')
        self.assertTrue(response['user']['twitter_username_verified'])

        # it's verified!!
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['nostr_public_key'], NOSTR_KEY_1)
        self.assertTrue(response['user']['nostr_public_key_verified'])
        """
        # sign up with Nostr
        token_nostr_user = self.nostr_auth(NOSTR_PRIVATE_KEY_2)

        # link a lnurl account
        code, response = self.put("/api/users/me/verify/lnurl", {},
            headers=self.get_auth_headers(token_nostr_user))
        self.assertEqual(code, 200)
        self.assertIn('k1', response)
        self.assertIn('svg', response['qr'])

        k1 = response['k1']

        self.assertNotIn(k1, self.returned_k1s)
        self.returned_k1s.add(k1)

        # not verified yet...
        code, response = self.put(f"/api/users/me/verify/lnurl", {'k1': k1},
            headers=self.get_auth_headers(token_nostr_user))
        self.assertEqual(code, 200)
        self.assertFalse(response['success'])

        # generate a key and sign the k1
        key = self.generate_lnauth_key()
        sig = key.sign_digest(bytes.fromhex(k1), sigencode=ecdsa.util.sigencode_der)

        # sign k1 and send the key and signature (note this is a GET request, done by the wallet, without the token!)
        code, response = self.get(f"/api/users/me/verify/lnurl",
            {'k1': k1,
             'key': key.verifying_key.to_string().hex(),
             'sig': sig.hex()})
        self.assertEqual(code, 200)

        # yep, we are verified now!
        code, response = self.put(f"/api/users/me/verify/lnurl", {'k1': k1},
            headers=self.get_auth_headers(token_nostr_user))
        self.assertEqual(code, 200)
        self.assertTrue(response['success'])

        token_nostr_user_logged_in_with_lnauth = self.lnurl_auth(key)

        # the identity of the user should be the same (whether logged in with nostr or with the newly linked lightning key)
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_nostr_user))
        self.assertEqual(code, 200)
        identity_nostr_user = response['user']['identity']
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_nostr_user_logged_in_with_lnauth))
        self.assertEqual(code, 200)
        identity_nostr_user_logged_in_with_lnauth = response['user']['identity']

        self.assertEqual(identity_nostr_user, identity_nostr_user_logged_in_with_lnauth)

        # create another user
        token_2 = self.nostr_auth(PrivateKey(), contribution_percent=1)

        # set user details
        code, response = self.update_user(token_2, twitter_username='username2')
        self.assertEqual(code, 200)

        # can't use the same Twitter username
        code, response = self.update_user(token_2, twitter_username='username1', expect_success=False)
        self.assertEqual(code, 400)
        self.assertIn("already registered", response['message'])

        # can't set the same email
        code, response = self.update_user(token_2, email="goodemail@plebeian.market", expect_success=False)
        self.assertEqual(code, 400)
        self.assertIn("already registered", response['message'])

        # ... but can set another email
        code, response = self.update_user(token_2, email="goodemail2@plebeian.market")
        self.assertEqual(code, 200)

        # 2nd user is not a moderator!
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['twitter_username'], 'username2')
        self.assertFalse(response['user']['twitter_username_verified'])
        self.assertEqual(response['user']['email'], "goodemail2@plebeian.market")
        self.assertIsNotNone(response['user']['contribution_percent'])

        identity_2 = response['user']['identity']

        self.assertNotEqual(identity_1, identity_2)

    def test_auctions(self):
        token_1 = self.nostr_auth(PrivateKey(), twitter_username='auction_user_1', contribution_percent=1, wallet=OTHER_XPUB)
        token_2 = self.nostr_auth(PrivateKey(), twitter_username='auction_user_2', wallet=OTHER_XPUB)

        # GET user auctions if not logged in is OK
        code, response = self.get("/api/users/auction_user_1/auctions")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 0)  # no auctions yet

        # creating auctions requires log in
        code, response = self.post("/api/users/me/auctions",
            {'starting_bid': 10})
        self.assertEqual(code, 401)
        self.assertFalse(response['success'])
        self.assertIn("missing token", response['message'].lower())

        # GET auctions if logged in as well to see there are none there
        code, response = self.get("/api/users/me/auctions",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 0)

        # can't create an auction without duration
        code, response = self.post("/api/users/me/auctions",
            {'title': "My 1st",
             'description': "Selling something",
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertIn("missing", response['message'].lower())
        self.assertIn("duration", response['message'].lower())

        # dates must be UTC
        code, response = self.post("/api/users/me/auctions",
            {'title': "My 1st",
             'description': "Selling something",
             'start_date': "2020-10-10T11:11:00",
             'duration_hours': 24,
             'shipping_domestic_usd': 5,
             'shipping_worldwide_usd': 10,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertIn("must be in utc", response['message'].lower())

        # finally create an auction (with token_1)
        code, response = self.post("/api/users/me/auctions",
            {'title': "My 1st",
             'description': "Selling something",
             'duration_hours': 0.003, # 10 seconds
             'shipping_domestic_usd': 5,
             'shipping_worldwide_usd': 10,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertIn('auction', response)

        auction_key = response['auction']['key']

        # fail to see auction that is not running yet by user that did not create it
        code, response = self.get("/api/users/auction_user_1/auctions?filter=new")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 0)

        # the user now has_items
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['has_items'], True)
        self.assertEqual(response['user']['has_own_items'], True)

        # GET auctions to find auction in our "not running" section
        code, response = self.get("/api/users/me/auctions?filter=new",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 1)
        self.assertEqual(response['auctions'][0]['key'], auction_key)
        self.assertEqual(response['auctions'][0]['started'], False)
        self.assertEqual(response['auctions'][0]['ended'], False)

        # GET the newly created auction by key (even unauthenticated!)
        code, response = self.get(f"/api/auctions/{auction_key}")
        self.assertEqual(code, 200)
        self.assertEqual(response['auction']['key'], auction_key)
        self.assertIsNone(response['auction']['nostr_event_id'])

        # create a 2nd auction, this time for the 2nd user
        code, response = self.post("/api/users/me/auctions",
            {'title': "His 2st",
             'description': "Selling something else",
             'duration_hours': 24,
             'shipping_domestic_usd': 5,
             'shipping_worldwide_usd': 10,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertIn('auction', response)

        auction_key_2 = response['auction']['key']

        # the two auctions differ indeed
        self.assertNotEqual(auction_key, auction_key_2)

        # listing one user's auctions does not return the other one
        code, response = self.get("/api/users/auction_user_2/auctions",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 1)
        self.assertEqual(response['auctions'][0]['key'], auction_key_2)

        # can't DELETE an auction if not logged in
        code, response = self.delete(f"/api/auctions/{auction_key_2}")
        self.assertEqual(code, 401)

        # also can't DELETE another user's auction
        code, response = self.delete(f"/api/auctions/{auction_key_2}",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 401)

        # also can't EDIT another user's auction
        code, response = self.put(f"/api/auctions/{auction_key_2}",
            {'starting_bid': 100},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 401)

        # can EDIT the auction with the proper user
        code, response = self.put(f"/api/auctions/{auction_key_2}",
            {'starting_bid': 888, 'key': 'NEW_KEY_WONT_WORK'},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)

        # GET the newly edited auction to see the new starting_bid
        # (note that the key did not change, since we can't edit the key!)
        code, response = self.get(f"/api/auctions/{auction_key_2}")
        self.assertEqual(code, 200)
        self.assertEqual(response['auction']['key'], auction_key_2) # didn't change
        self.assertEqual(response['auction']['starting_bid'], 888)

        # can DELETE the auction with the proper auth headers
        code, response = self.delete(f"/api/auctions/{auction_key_2}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)

        # can't GET the deleted auction anymore
        code, response = self.get(f"/api/auctions/{auction_key_2}")
        self.assertEqual(code, 404)

        # publish the auction
        code, response = self.put(f"/api/auctions/{auction_key}/publish", {},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # GET the auction that we just started
        code, response = self.get(f"/api/auctions/{auction_key}")
        self.assertEqual(code, 200)
        auction_merchant_public_key = response['auction']['merchant_public_key']
        auction_initial_nostr_event_id = response['auction']['nostr_event_id']
        self.assertIsNotNone(auction_initial_nostr_event_id)

        bid_event = Event(kind=BID_NOSTR_EVENT_KIND, content="888")
        NOSTR_BUYER_PRIVATE_KEY.sign_event(bid_event)
        signed_event_json = json.loads(bid_event.to_message())[1]

        copy_of_signed_event_json = dict(signed_event_json)
        copy_of_signed_event_json['sig'] = "12345"
        code, response = self.post(f"/api/merchants/{auction_merchant_public_key}/auctions/{auction_initial_nostr_event_id}/bids", copy_of_signed_event_json)
        self.assertEqual(code, 400)
        self.assertIn("invalid event signature", response['message'].lower())

        copy_of_signed_event_json = dict(signed_event_json)
        copy_of_signed_event_json['content'] = "999" # trying to change the amount after it was signed...
        code, response = self.post(f"/api/merchants/{auction_merchant_public_key}/auctions/{auction_initial_nostr_event_id}/bids", copy_of_signed_event_json)
        self.assertEqual(code, 400)
        self.assertIn("invalid event id", response['message'].lower())

        # can still EDIT the auction once started
        code, response = self.put(f"/api/auctions/{auction_key}",
            {'starting_bid': 101},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # GET the auction again after edit
        code, response = self.get(f"/api/auctions/{auction_key}")
        self.assertEqual(code, 200)

        auction_after_edit_nostr_event_id = response['auction']['nostr_event_id']
        self.assertIsNotNone(auction_after_edit_nostr_event_id)
        self.assertNotEqual(auction_after_edit_nostr_event_id, auction_initial_nostr_event_id)

        token_3 = self.nostr_auth(PrivateKey())

        # place a bid
        code, response = self.post(f"/api/merchants/{auction_merchant_public_key}/auctions/{auction_after_edit_nostr_event_id}/bids", signed_event_json)
        self.assertEqual(code, 200)

        # cannot place a huge bid
        above_threshold_usd = app.config['SKIN_IN_THE_GAME_THRESHOLDS'][0]['bid_amount_usd'] + 1
        above_threshold_sats = int(ONE_DOLLAR_SATS * above_threshold_usd)
        huge_bid_event = Event(kind=BID_NOSTR_EVENT_KIND, content=str(above_threshold_sats))
        NOSTR_BUYER_PRIVATE_KEY.sign_event(huge_bid_event)
        signed_huge_event_json = json.loads(huge_bid_event.to_message())[1]
        code, response = self.post(f"/api/merchants/{auction_merchant_public_key}/auctions/{auction_after_edit_nostr_event_id}/bids", signed_huge_event_json)
        self.assertEqual(code, 400)
        self.assertIn("skin in the game", response['message'].lower())

        # cannot EDIT the auction anymore once it has a bid
        code, response = self.put(f"/api/auctions/{auction_key}",
            {'starting_bid': 102},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 403)
        self.assertIn("cannot edit auctions that already have bids", response['message'].lower())

        # also can't DELETE the auction once it has bids
        code, response = self.delete(f"/api/auctions/{auction_key}",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 403)
        self.assertIn("cannot edit auctions that already have bids", response['message'].lower())

        # auction has a bid!
        code, response = self.get(f"/api/auctions/{auction_key}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auction']['bids']), 1)
        self.assertIsNone(response['auction']['has_winner'])

        # can't place a bid lower than the previous one now
        lower_bid_event = Event(kind=BID_NOSTR_EVENT_KIND, content="777")
        NOSTR_BUYER_PRIVATE_KEY.sign_event(lower_bid_event)
        signed_lower_event_json = json.loads(lower_bid_event.to_message())[1]
        code, response = self.post(f"/api/merchants/{auction_merchant_public_key}/auctions/{auction_after_edit_nostr_event_id}/bids", signed_lower_event_json)
        self.assertEqual(code, 400)
        self.assertIn("your bid needs to be higher", response['message'].lower())

        # create an auction without a start date
        code, response = self.post("/api/users/me/auctions",
            {'title': "Auction without start date",
             'description': "Selling something on Twitter",
             'duration_hours': 24,
             'shipping_domestic_usd': 5,
             'shipping_worldwide_usd': 10,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertIn('auction', response)

        auction_key_3 = response['auction']['key']

        # another user can't start my auction
        code, response = self.put(f"/api/auctions/{auction_key_3}/publish", {},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 401)

        # start the auction
        code, response = self.put(f"/api/auctions/{auction_key_3}/publish", {},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)

        time.sleep(1) # this is not needed for the start to work, but we use it to make sure start_date is in the past

        code, response = self.get(f"/api/auctions/{auction_key_3}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertIn('auction', response)
        self.assertTrue(response['auction']['start_date'] < (datetime.utcnow().isoformat() + "Z"))
        self.assertEqual(response['auction']['started'], True)
        self.assertEqual(response['auction']['ended'], False)
        self.assertEqual(dateutil.parser.isoparse(response['auction']['start_date']) + timedelta(hours=24), dateutil.parser.isoparse(response['auction']['end_date']))

        # Create an auction with malicious input to description
        malicious_desc = '''<script type="text/javascript">alert("malicious")</script>'''
        code, response = self.post("/api/users/me/auctions",
            {'title': "My 1st",
             'description': malicious_desc,
             'start_date': (datetime.utcnow() + timedelta(days=1)).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
             'duration_hours': 24,
             'shipping_domestic_usd': 5,
             'shipping_worldwide_usd': 10,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertIn('auction', response)
        cleaned_description = response['auction']['description']
        expected_cleaned_description = """&lt;script type="text/javascript"&gt;alert("malicious")&lt;/script&gt;"""
        self.assertEqual(cleaned_description, expected_cleaned_description)

        app.logger.warning("Waiting for the auction to finalize...")
        time.sleep(15)

        # now the auction appears under "inactive auctions" rather than under "active"
        code, response = self.get("/api/auctions/inactive")
        self.assertEqual(code, 200)
        self.assertIn(auction_key, [a['key'] for a in response['auctions']])
        code, response = self.get("/api/auctions/active")
        self.assertEqual(code, 200)
        self.assertNotIn(auction_key, [a['key'] for a in response['auctions']])

        # auction should have a winner now
        code, response = self.get(f"/api/auctions/{auction_key}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auction']['bids']), 1)
        self.assertTrue(response['auction']['has_winner'])

        # another user can also see the auction has a winner
        code, response = self.get(f"/api/auctions/{auction_key}",
            headers=self.get_auth_headers(token_3))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auction']['bids']), 1)
        self.assertTrue(response['auction']['has_winner'])
