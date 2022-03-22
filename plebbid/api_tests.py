from datetime import datetime, timedelta

import unittest
import requests

from plebbid.main import app

class TestApi(unittest.TestCase):
    def do(self, f, path, params=None, data=None):
        BASE_URL = app.config['BASE_URL']
        response = f(f"{BASE_URL}{path}", params=params, data=data)
        return response.status_code, response.json() if response.status_code in (200, 400, 404) else None

    def get(self, path, params=None):
        return self.do(requests.get, path, params=params)

    def post(self, path, data):
        return self.do(requests.post, path, data=data)

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

    def test_21_login(self):
        code, response = self.get("/login")
        self.assertEqual(code, 200)
        self.assertTrue('svg' in response['qr'])

        code, response = self.get("/login",
            {'k1': "b29fa5994dc9da9906a36f996e6ac4faa2b0e2601ef13b0fab9d4b4287c57e1f",
             'key': "030f12794ae14407b8e1bfa1cbc297bb68ce6b24455ceab52c02da7a92782b6b14",
             'sig': "4045022100a23fbcaf3f24aff085d8c86a744764be8390e8511eca675ae2af037f33ff1a92022035f00465fbcad73e3175d7dc2e891322fa9dcce7bbd19409866f855e6da1f51e"})
        self.assertEqual(code, 400)
        self.assertTrue("verification failed" in response['message'].lower())

        code, response = self.get("/login",
            {'k1': "b29fa5994dc9da9906a36f996e6ac4faa2b0e2601ef13b0fab9d4b4287c57e1f",
             'key': "030f12794ae14407b8e1bfa1cbc297bb68ce6b24455ceab52c02da7a92782b6b14",
             'sig': "3045022100a23fbcaf3f24aff085d8c86a744764be8390e8511eca675ae2af037f33ff1a92022035f00465fbcad73e3175d7dc2e891322fa9dcce7bbd19409866f855e6da1f51e"})
        self.assertEqual(code, 200)
        self.assertTrue('token' in response)
