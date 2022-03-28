from datetime import datetime, timedelta

import ecdsa
import unittest
import requests

from plebbid.main import app

class TestApi(unittest.TestCase):
    def do(self, f, path, params=None, data=None, headers=None):
        BASE_URL = app.config['BASE_URL']
        response = f(f"{BASE_URL}{path}", params=params, data=data, headers=headers)
        return response.status_code, response.json() if response.status_code in (200, 400, 404) else None

    def get(self, path, params=None):
        return self.do(requests.get, path, params=params)

    def post(self, path, data, headers=None):
        return self.do(requests.post, path, data=data, headers=headers)

    def delete(self, path):
        return self.do(requests.delete, path)

    def test_01_seller(self):
        # create a seller
        code, response = self.post("/sellers", {'key': 'SELLER_KEY_1'})
        self.assertEqual(code, 200)
        self.assertEqual(response.get('success'), True)

        # create a dupe seller
        code, response = self.post("/sellers", {'key': 'SELLER_KEY_1'})
        self.assertEqual(code, 400)
        self.assertEqual(response.get('success'), False)
        self.assertTrue("already" in response.get('message'))

    def test_11_seller_auctions(self):
        # GET seller auctions to see there are none
        code, response = self.get("/sellers/SELLER_KEY_1/auctions")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 0)

        # can't GET auctions for missing seller
        code, response = self.get("/sellers/SELLER_KEY_MISSING/auctions")
        self.assertEqual(code, 404)

        # can't create an auction without dates
        code, response = self.post("/sellers/SELLER_KEY_1/auctions", {'minimum_bid': 10})
        self.assertEqual(code, 400)
        self.assertTrue("missing" in response.get('message', '').lower())
        self.assertTrue("starts_at" in response.get('message'))

        # can't create an auction in the past
        code, response = self.post("/sellers/SELLER_KEY_1/auctions", {'starts_at': "2020-10-10", 'ends_at': "2020-10-11", 'minimum_bid': 10})
        self.assertEqual(code, 400)
        self.assertTrue("must be in the future" in response.get('message', '').lower())

        # create an auction
        code, response = self.post("/sellers/SELLER_KEY_1/auctions", {'starts_at': (datetime.utcnow() + timedelta(days=1)).isoformat(), 'ends_at': (datetime.utcnow() + timedelta(days=2)).isoformat(), 'minimum_bid': 10})
        self.assertEqual(code, 200)
        auction_key = response.get('key')
        auction_short_id = response.get('short_id')

        # GET seller auctions to find our auction
        code, response = self.get("/sellers/SELLER_KEY_1/auctions")
        self.assertEqual(code, 200)
        self.assertEqual(len(response['auctions']), 1)
        self.assertEqual(response['auctions'][0].get('short_id'), auction_short_id)
        self.assertEqual(response['auctions'][0].get('key'), auction_key)

        # GET the newly created auction by short_id
        code, response = self.get(f"/sellers/SELLER_KEY_1/auctions/{auction_short_id}")
        self.assertEqual(code, 200)
        self.assertEqual(response['auction'].get('short_id'), auction_short_id)
        self.assertEqual(response['auction'].get('key'), auction_key)

        # GET the newly created auction by key
        code, response = self.get(f"/auctions/{auction_key}")
        self.assertEqual(code, 200)
        self.assertEqual(response['auction'].get('short_id'), auction_short_id)
        self.assertEqual(response['auction'].get('key'), auction_key)

        # create a 2nd auction
        code, response = self.post("/sellers/SELLER_KEY_1/auctions", {'starts_at': (datetime.utcnow() + timedelta(days=1)).isoformat(), 'ends_at': (datetime.utcnow() + timedelta(days=2)).isoformat(), 'minimum_bid': 10})
        self.assertEqual(code, 200)
        auction_key_2 = response.get('key')
        auction_short_id_2 = response.get('short_id')

        # the two auctions differ indeed
        self.assertNotEqual(auction_key, auction_key_2)
        self.assertNotEqual(auction_short_id, auction_short_id_2)

        # can't DELETE an auction using the auction key
        code, response = self.delete(f"/auctions/{auction_key}")
        self.assertEqual(code, 405)

        # can DELETE an auction using the seller key and short ID
        code, response = self.delete(f"/sellers/SELLER_KEY_1/auctions/{auction_short_id_2}")
        self.assertEqual(code, 200)

        # can't GET the deleted auction anymore
        code, response = self.get(f"/sellers/SELLER_KEY_1/auctions/{auction_short_id_2}")
        self.assertEqual(code, 404)

        # log in with Lightning
        code, response = self.get("/login")
        self.assertEqual(code, 200)
        self.assertTrue('k1' in response and 'svg' in response['qr'])

        k1 = response['k1']

        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        sig = sk.sign_digest(bytes.fromhex(k1), sigencode=ecdsa.util.sigencode_der)

        # not logged in yet...
        code, response = self.get("/login", {'k1': k1})
        self.assertEqual(code, 200)
        self.assertFalse(response['success'])

        # try sending another k1 (but properly signed)...
        another_k1 = list(bytes.fromhex(k1))
        another_k1[0] = (another_k1[0] + 1) % 255
        another_k1 = bytes(another_k1)
        another_sig = sk.sign_digest(another_k1, sigencode=ecdsa.util.sigencode_der)
        code, response = self.get("/login", {'k1': another_k1.hex(), 'key': sk.verifying_key.to_string().hex(), 'sig': another_sig.hex()})
        self.assertEqual(code, 400)
        self.assertTrue('invalid challenge' in response['message'].lower())

        # try sending a wrong signature
        code, response = self.get("/login", {'k1': k1, 'key': sk.verifying_key.to_string().hex(), 'sig': another_sig.hex()})
        self.assertEqual(code, 400)
        self.assertTrue('verification failed' in response['message'].lower())

        code, response = self.get("/login", {'k1': k1, 'key': sk.verifying_key.to_string().hex(), 'sig': sig.hex()})
        self.assertEqual(code, 200)
        self.assertTrue('token' in response)

        token = response['token']

        # since we are signed in, no we can get a token even without providing a key,
        # but we should eventually delete the lnauth from the DB, maybe after 1st successful authenticated request?
        code, response = self.get("/login", {'k1': k1})
        self.assertEqual(code, 200)
        self.assertEqual(response['token'], token)

        # anonymous users can't place a bid
        code, response = self.post(f"/auctions/{auction_key}/bids", {'amount': 100})
        self.assertEqual(code, 400)
        self.assertTrue('missing token' in response['message'].lower())

        # users can place a bid
        code, response = self.post(f"/auctions/{auction_key}/bids", {'amount': 888}, {'x-access-tokens': token})
        self.assertEqual(code, 200)
        self.assertTrue('payment_request' in response)

