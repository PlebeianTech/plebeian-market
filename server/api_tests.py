from datetime import datetime, timedelta
import time

import dateutil.parser
import ecdsa
import unittest
import requests

from server.main import app

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
        self.assertTrue('invalid challenge' in response['message'].lower())

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
        self.assertTrue('token' in response)

        token_1 = response['token']

        # since we are signed in, now we can get a token even without providing a key,
        # but we should eventually delete the lnauth from the DB, maybe after 1st successful authenticated request?
        code, response = self.get("/api/login", {'k1': k1},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(response['token'], token_1)

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
            {'minimum_bid': 10})
        self.assertEqual(code, 401)
        self.assertFalse(response['success'])
        self.assertTrue("missing token" in response['message'].lower())

        # GET auctions to see there are none there
        code, response = self.get("/api/auctions",
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 0)

        # can't create an auction without dates
        code, response = self.post("/api/auctions",
            {'minimum_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertTrue("missing" in response['message'].lower())
        self.assertTrue("starts_at" in response['message'])

        # dates must be UTC
        code, response = self.post("/api/auctions",
            {'starts_at': "2020-10-10T11:11:00",
             'ends_at': "2020-10-11T11:11:00",
             'minimum_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertTrue("must be in utc" in response['message'].lower())

        # can't create an auction that ends before it starts
        code, response = self.post("/api/auctions",
            {'starts_at': "2020-10-11T11:11:00Z",
             'ends_at': "2020-10-10T11:11:00Z",
             'minimum_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 400)
        self.assertTrue("must be after" in response['message'].lower())

        # finally create an auction
        code, response = self.post("/api/auctions",
            {'starts_at': (datetime.utcnow() + timedelta(days=1)).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
             'ends_at': (datetime.utcnow() + timedelta(days=2)).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
             'minimum_bid': 10},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)
        self.assertTrue('auction' in response)

        auction_key = response['auction']['key']

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
            {'starts_at': (datetime.utcnow() + timedelta(days=1)).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
             'ends_at': (datetime.utcnow() + timedelta(days=2)).replace(tzinfo=dateutil.tz.tzutc()).isoformat(),
             'minimum_bid': 10},
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
            {'minimum_bid': 100},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 401)

        # can EDIT the auction with the proper user
        code, response = self.put(f"/api/auctions/{auction_key_2}",
            {'minimum_bid': 888, 'key': 'NEW_KEY_WONT_WORK'},
            headers=self.get_auth_headers(token_2))
        self.assertEqual(code, 200)

        # GET the newly edited auction to see the new minimum_bid
        # (note that the key did not change, since we can't edit the key!)
        code, response = self.get(f"/api/auctions/{auction_key_2}")
        self.assertEqual(code, 200)
        self.assertEqual(response['auction']['key'], auction_key_2)
        self.assertEqual(response['auction']['minimum_bid'], 888)

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
        app.logger.warning(response)
        self.assertTrue('not running' in response['message'].lower())

        code, response = self.put(f"/api/auctions/{auction_key}",
            {'starts_at': (datetime.utcnow() - timedelta(days=1)).replace(tzinfo=dateutil.tz.tzutc()).isoformat()},
            headers=self.get_auth_headers(token_1))
        self.assertEqual(code, 200)

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
