from datetime import datetime, timedelta
import time

import dateutil.parser
import ecdsa
import unittest
import requests

from main import app

class TestApi(unittest.TestCase):
    def do(self, f, path, params=None, json=None, headers=None):
        BASE_URL = app.config['BASE_URL']
        response = f(f"{BASE_URL}{path}", params=params, json=json, headers=headers)
        return response.status_code, response.json() if response.status_code in (200, 400, 401, 403, 404) else None

    def get(self, path, params=None, headers=None):
        return self.do(requests.get, path, params=params, headers=headers)

    def post(self, path, json, headers=None):
        return self.do(requests.post, path, json=json, headers=headers)

    def put(self, path, json, headers=None):
        return self.do(requests.put, path, json=json, headers=headers)

    def delete(self, path, headers=None):
        return self.do(requests.delete, path, headers=headers)

    def get_auth_headers(self, token):
        return {'X-Access-Token': token}

    def test_11_api(self):
        code, response = self.get("/api/login")
        self.assertEqual(code, 200)
        self.assertTrue('k1' in response and 'svg' in response['qr'])

        k1 = response['k1']

        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        sig = sk.sign_digest(bytes.fromhex(k1), sigencode=ecdsa.util.sigencode_der)

        # not logged in yet...
        code, response = self.get("/api/login", {'k1': k1})
        self.assertEqual(code, 200)
        self.assertFalse(response['success'])

        # try sending another k1 (but properly signed)...
        another_k1 = list(bytes.fromhex(k1))
        another_k1[0] = (another_k1[0] + 1) % 255
        another_k1 = bytes(another_k1)
        another_sig = sk.sign_digest(another_k1, sigencode=ecdsa.util.sigencode_der)
        code, response = self.get("/api/login",
            {'k1': another_k1.hex(),
             'key': sk.verifying_key.to_string().hex(),
             'sig': another_sig.hex()})
        self.assertEqual(code, 400)
        self.assertTrue('verification failed' in response['message'].lower())

        # try sending a wrong signature
        code, response = self.get("/api/login",
            {'k1': k1,
             'key': sk.verifying_key.to_string().hex(),
             'sig': another_sig.hex()})
        self.assertEqual(code, 400)
        self.assertTrue('verification failed' in response['message'].lower())

        code, response = self.get("/api/login",
            {'k1': k1,
             'key': sk.verifying_key.to_string().hex(),
             'sig': sig.hex()})
        self.assertEqual(code, 200)
        self.assertTrue('token' not in response)

        code, response = self.get("/api/login",
            {'k1': k1})
        self.assertEqual(code, 200)
        self.assertTrue('token' in response)
        self.assertTrue('user' in response)
        self.assertIsNone(response['user']['twitter_username'])
        self.assertIsNone(response['user']['contribution_percent'])

        token_1 = response['token']

        # can't request the token again if we already got it once
        code, response = self.get("/api/login",
            {'k1': k1,
             'key': sk.verifying_key.to_string().hex(),
             'sig': sig.hex()},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)

        # no user details set yet
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertIsNone(response['user']['twitter_username'])
        self.assertIsNone(response['user']['contribution_percent'])

        # set user details
        code, response = self.post("/api/users/me",
            {'twitter_username': 'hellokitty', 'contribution_percent': 1},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # check user details again
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['twitter_username'], 'hellokitty')
        self.assertTrue("lorem.space" in response['user']['twitter_profile_image_url'])
        self.assertEqual(response['user']['contribution_percent'], 1)
        self.assertEqual(response['user']['has_auctions'], False)

        # create another user
        code, response = self.get("/api/login")
        self.assertEqual(code, 200)
        self.assertTrue('k1' in response and 'svg' in response['qr'])

        k1_2 = response['k1']

        self.assertNotEqual(k1, k1_2)

        sk_2 = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        sig_2 = sk_2.sign_digest(bytes.fromhex(k1_2), sigencode=ecdsa.util.sigencode_der)

        code, response = self.get("/api/login",
            {'k1': k1_2,
             'key': sk_2.verifying_key.to_string().hex(),
             'sig': sig_2.hex()})
        self.assertEqual(code, 200)
        self.assertTrue('token' not in response)

        code, response = self.get("/api/login",
            {'k1': k1_2})
        self.assertEqual(code, 200)
        self.assertTrue('token' in response)

        token_2 = response['token']

        self.assertNotEqual(token_1, token_2)

        # GET auctions requires log in
        code, response = self.get("/api/auctions")
        self.assertEqual(code, 401)
        self.assertFalse(response['success'])
        self.assertTrue("missing token" in response['message'].lower())

        # creating auctions requires log in
        code, response = self.post("/api/auctions",
            {'starting_bid': 10})
        self.assertEqual(code, 401)
        self.assertFalse(response['success'])
        self.assertTrue("missing token" in response['message'].lower())

        # GET auctions to see there are none there
        code, response = self.get("/api/auctions",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 0)

        # can't create an auction without dates or duration
        code, response = self.post("/api/auctions",
            {'title': "My 1st",
             'description': "Selling something",
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertTrue("missing" in response['message'].lower())
        self.assertTrue("duration" in response['message'].lower())

        # dates must be UTC
        code, response = self.post("/api/auctions",
            {'title': "My 1st",
             'description': "Selling something",
             'start_date': "2020-10-10T11:11:00",
             'duration_hours': 24,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertTrue("must be in utc" in response['message'].lower())

        # finally create an auction
        code, response = self.post("/api/auctions",
            {'title': "My 1st",
             'description': "Selling something",
             'start_date': (datetime.utcnow() + timedelta(days=1)).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
             'duration_hours': 24,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertTrue('auction' in response)

        auction_key = response['auction']['key']

        # the user now has_auctions
        code, response = self.get("/api/users/me",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['user']['has_auctions'], True)

        # GET auctions to find our auction
        code, response = self.get("/api/auctions",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 1)
        self.assertEqual(response['auctions'][0]['key'], auction_key)

        # GET the newly created auction by key (even unauthenticated!)
        code, response = self.get(f"/api/auctions/{auction_key}")
        self.assertEqual(code, 200)
        self.assertEqual(response['auction']['key'], auction_key)

        # create a 2nd auction, this time for the 2nd user
        code, response = self.post("/api/auctions",
            {'title': "His 2st",
             'description': "Selling something else",
             'start_date': (datetime.utcnow() + timedelta(days=1)).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
             'duration_hours': 24,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertTrue('auction' in response)

        auction_key_2 = response['auction']['key']

        # the two auctions differ indeed
        self.assertNotEqual(auction_key, auction_key_2)

        # listing one user's auctions does not return the other one
        code, response = self.get("/api/auctions",
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

        # CANCEL an auction
        code, response = self.put(f"/api/auctions/{auction_key_2}",
            {'canceled': True},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)

        # can not un-CANCEL an auction
        code, response = self.put(f"/api/auctions/{auction_key_2}",
            {'canceled': False},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 400)
        self.assertTrue("can not un-cancel" in response['message'].lower())

        # can not EDIT a canceled auction
        code, response = self.put(f"/api/auctions/{auction_key_2}",
            {'starting_bid': 777},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 403)
        self.assertTrue("edit a canceled auction", response['message'].lower())

        # can DELETE the auction with the proper auth headers
        code, response = self.delete(f"/api/auctions/{auction_key_2}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)

        # can't GET the deleted auction anymore
        code, response = self.get(f"/api/auctions/{auction_key_2}")
        self.assertEqual(code, 404)

        # anonymous users can't place a bid
        code, response = self.post(f"/api/auctions/{auction_key}/bids", {'amount': 100})
        self.assertEqual(code, 401)
        self.assertTrue('missing token' in response['message'].lower())

        # can't place a bid because the auction has not started yet
        code, response = self.post(f"/api/auctions/{auction_key}/bids", {'amount': 888},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 403)
        self.assertTrue('not running' in response['message'].lower())

        # start the auction
        code, response = self.put(f"/api/auctions/{auction_key}",
            {'start_date': (datetime.utcnow() - timedelta(days=1)).replace(tzinfo=dateutil.tz.tzutc()).isoformat()},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        # can't EDIT the auction once started
        code, response = self.put(f"/api/auctions/{auction_key}",
            {'starting_bid': 101},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 403)
        self.assertTrue('cannot edit an auction once started' in response['message'].lower())

        # users can place a bid
        code, response = self.post(f"/api/auctions/{auction_key}/bids", {'amount': 888},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertTrue('payment_request' in response)
        self.assertTrue(response['payment_request'].startswith('MOCK'))
        self.assertTrue('svg' in response['qr'])

        bid_payment_request = response['payment_request']

        # auction has no (settled) bids... yet
        code, response = self.get(f"/api/auctions/{auction_key}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auction']['bids']), 0)

        # waiting for the invoice to settle...
        time.sleep(4)

        # auction has our settled bid!
        code, response = self.get(f"/api/auctions/{auction_key}",
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auction']['bids']), 1)
        self.assertEqual(response['auction']['bids'][0]['payment_request'], bid_payment_request)

        # can't place a bid lower than the previous one now
        code, response = self.post(f"/api/auctions/{auction_key}/bids", {'amount': 777},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 400)
        self.assertTrue('amount needs to be at least' in response['message'].lower())

        # create an auction without a start date
        code, response = self.post("/api/auctions",
            {'title': "Auction without start date",
             'description': "Selling something on Twitter",
             'duration_hours': 24,
             'starting_bid': 10,
             'reserve_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertTrue('auction' in response)

        auction_key_3 = response['auction']['key']

        # another user can't start my auction
        code, response = self.put(f"/api/auctions/{auction_key_3}/start-twitter", {},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 401)

        # start the auction by getting images from Twitter
        code, response = self.put(f"/api/auctions/{auction_key_3}/start-twitter", {},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

        time.sleep(1) # this is not needed for the start to work, but we use it to make sure start_date is in the past

        code, response = self.get(f"/api/auctions/{auction_key_3}",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertTrue('auction' in response)
        self.assertTrue(response['auction']['start_date'] < (datetime.utcnow().isoformat() + "Z"))
        self.assertEqual(dateutil.parser.isoparse(response['auction']['start_date']) + timedelta(hours=24), dateutil.parser.isoparse(response['auction']['end_date']))
        self.assertEqual(len(response['auction']['media']), 2)
        self.assertTrue("logo" in response['auction']['media'][0]['url']) # this one comes from MockTwitter
