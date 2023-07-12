from aiofile import async_open
import aiohttp
from aiohttp import web
import argparse
import asyncio
from datetime import datetime, timedelta
from enum import IntEnum
import json
import logging
from logging.config import dictConfig
import os
import os.path
import requests
import sys
import time
from typing import List
import websockets

BIRDWATCHER_PORT = 6000

API_BASE_URL = os.environ.get('API_BASE_URL')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
PROCESSED_EVENT_IDS_FILENAME = os.environ.get('PROCESSED_EVENT_IDS_FILENAME')

dictConfig({
    'version': 1,
    'formatters': {'default': {'format': "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}},
    'handlers': {'default': {'class': 'logging.StreamHandler', 'formatter': 'default'}},
    'root': {'level': LOG_LEVEL, 'handlers': ['default']},
})

class EventKind(IntEnum):
    DM = 4
    STALL = 30017
    AUCTION = 30020
    BID = 1021

class Relay:
    def __init__(self, url, args, processed_event_ids):
        self.url = url
        self.args = args
        self.processed_event_ids = processed_event_ids

        self.subscribed_auction_event_ids = set()
        self.subscribed_merchant_pubkeys = set()
        self.auction_owners = {} # event ID to pubkey

    async def check_ours(self, event, cb):
        async def do_get(session, url):
            async with session.get(url) as response:
                if response.status == 404:
                    logging.debug(f"Not our merchant {event['pubkey']}...")
                elif response.status == 200:
                    await cb(**event)
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(do_get(session, f"{API_BASE_URL}/api/merchants/{event['pubkey']}"))

    async def post_dm(self, merchant_pubkey, dm_event, all_relays):
        async def do_post(session, url, json):
            async with session.post(url, json=json) as response:
                logging.debug(f"POST to merchant {merchant_pubkey}: {dm_event}")
                if response.status == 200:
                    logging.info(f"Forwarded message to merchant {merchant_pubkey}.")
                elif response.status == 409:
                    logging.info(f"Order already exists at {merchant_pubkey}.")
                elif response.status in [400, 403, 404, 500]:
                    logging.error(f"Error posting to merchant {merchant_pubkey}: {response.status}.")
                try:
                    response_json = await response.json()
                    logging.debug(f"POST responded with {response_json}!")
                except Exception:
                    response_text = await response.text()
                    logging.debug(f"POST responded with {response_text}!")
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(do_post(session, f"{API_BASE_URL}/api/merchants/{merchant_pubkey}/messages", dm_event))

    async def post_bid(self, auction_event_id, bid_event, all_relays):
        merchant_pubkey = self.auction_owners[auction_event_id]
        async def do_post(session, url, json):
            async with session.post(url, json=json) as response:
                logging.debug(f"POST to auction {auction_event_id} of merchant {merchant_pubkey}: {bid_event}")
                if response.status == 200:
                    logging.info(f"Forwarded bid to auction {auction_event_id} of merchant {merchant_pubkey}.")
                elif response.status in [400, 403, 404, 500]:
                    logging.error(f"Error posting bid to auction {auction_event_id} of merchant {merchant_pubkey}: {response.status}.")
                try:
                    response_json = await response.json()
                    logging.debug(f"POST responded with {response_json}!")
                except Exception:
                    response_text = await response.text()
                    logging.debug(f"POST responded with {response_text}!")
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(do_post(session, f"{API_BASE_URL}/api/merchants/{merchant_pubkey}/auctions/{auction_event_id}/bids", bid_event))

    async def subscribe_stall(self):
        logging.info(f"({self.url}) Subscribing for stall events...")
        subscription_id = os.urandom(10).hex()
        await self.ws.send(json.dumps(['REQ', subscription_id, {'kinds': [EventKind.STALL]}]))
        return subscription_id

    async def subscribe_auction(self):
        logging.info(f"({self.url}) Subscribing for auction events...")
        subscription_id = os.urandom(10).hex()
        await self.ws.send(json.dumps(['REQ', subscription_id, {'kinds': [EventKind.AUCTION]}]))
        return subscription_id

    async def subscribe_dm(self, pubkey, **_):
        if pubkey not in self.subscribed_merchant_pubkeys:
            self.subscribed_merchant_pubkeys.add(pubkey)
            logging.info(f"({self.url}) Subscribing to DMs for merchant #p={pubkey}...")
            subscription_id = os.urandom(10).hex()
            await self.ws.send(json.dumps(['REQ', subscription_id, {"#p": [pubkey], 'kinds': [EventKind.DM]}]))
            return subscription_id

    async def subscribe_bids(self, pubkey, id, **_):
        if id not in self.subscribed_auction_event_ids:
            self.subscribed_auction_event_ids.add(id)
            assert id not in self.auction_owners
            self.auction_owners[id] = pubkey
            logging.info(f"({self.url}) Subscribing to bids for auction #e={id} of merchant {pubkey}...")
            subscription_id = os.urandom(10).hex()
            await self.ws.send(json.dumps(['REQ', subscription_id, {"#e": [id], 'kinds': [EventKind.BID]}]))
            return subscription_id

    async def send_event(self, event):
        if self.ws is not None:
            logging.info(f"({self.url}) Sending event {event['id']}...")
            await self.ws.send(json.dumps(['EVENT', event]))

    async def listen(self, all_relays):
        while True:
            logging.info(f"({self.url}) Connecting...")
            try:
                self.ws = await websockets.connect(self.url)
            except Exception:
                logging.exception(f"({self.url}) Cannot connect.")
                return

            try:
                if self.args.merchant:
                    await self.subscribe_dm(self.args.merchant)

                    if self.args.auction:
                        await self.subscribe_bids(self.args.merchant, self.args.auction)

                if self.args.discover:
                    await self.subscribe_auction()
                    await self.subscribe_stall()
            except Exception:
                logging.exception(f"({self.url}) Cannot subscribe.")
                return

            try:
                async for message in self.ws:
                    logging.debug(f"({self.url}) Received: {message}!")
                    message = json.loads(message)
                    if message[0] == 'EVENT':
                        event = message[2]
                        match event['kind']:
                            case EventKind.AUCTION:
                                try:
                                    auction = json.loads(event['content'])
                                except:
                                    auction = None
                                if isinstance(auction, dict) and 'start_date' in auction and 'duration' in auction:
                                    if datetime.fromtimestamp(auction['start_date']) + timedelta(seconds=auction['duration']) > datetime.utcnow():
                                        await self.check_ours(event, self.subscribe_bids)
                            case EventKind.STALL:
                                await self.check_ours(event, self.subscribe_dm)
                            case EventKind.DM:
                                if event['id'] not in self.processed_event_ids:
                                    self.processed_event_ids.add(event['id'])
                                    async with async_open(PROCESSED_EVENT_IDS_FILENAME, 'a') as f:
                                        await f.write(f"{event['id']}\n")
                                    merchant_pubkey = [t for t in event['tags'] if t[0] == 'p'][0][1]
                                    await self.post_dm(merchant_pubkey, event, all_relays)
                                else:
                                    logging.info(f"({self.url}) Skipping DM event: {event['id']}")
                            case EventKind.BID:
                                if event['id'] not in self.processed_event_ids:
                                    self.processed_event_ids.add(event['id'])
                                    async with async_open(PROCESSED_EVENT_IDS_FILENAME, 'a') as f:
                                        await f.write(f"{event['id']}\n")
                                    auction_event_id = [t for t in event['tags'] if t[0] == 'e'][0][1]
                                    await self.post_bid(auction_event_id, event, all_relays)
                                else:
                                    logging.info(f"({self.url}) Skipping bid event: {event['id']}")
            except Exception:
                self.ws = None
                logging.exception(f"({self.url}) Connection closed.")
                await asyncio.sleep(10)

async def main(relays):
    for relay in relays:
        asyncio.create_task(relay.listen(relays))

    app = web.Application()
    routes = web.RouteTableDef()

    @routes.post("/events")
    async def post_event(request):
        event_json = await request.json()
        logging.info(f"Forwarding event to all relays: {event_json['id']}!")
        for relay in relays:
            try:
                await relay.send_event(event_json)
            except Exception:
                logging.exception(f"Error forwarding event {event_json['id']} to {relay.url}!")
        return web.json_response({})
    @routes.post("/relays")
    async def post_relay(request):
        relay_json = await request.json()
        logging.info(f"Adding new relay: {relay_json['url']}!")
        try:
            relay = Relay(relay_json['url'], args, processed_event_ids)
            relays.append(relay)
            asyncio.create_task(relay.listen(relays))
            return web.json_response({})
        except Exception:
            logging.exception(f"Error adding relay: {relay['url']}!")
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", BIRDWATCHER_PORT)
    await site.start()

    await asyncio.Future()

parser = argparse.ArgumentParser(
    prog="Plebeian Market BirdWatcher",
    description="Watches Nostr relays for certain events needed by Plebeian Market to function")
parser.add_argument("-r", "--relay", help="relay to connect to")
parser.add_argument("--discover", default=True, help="discover stalls and auctions", action=argparse.BooleanOptionalAction)
parser.parse_args(["--no-discover"])
parser.add_argument("-m", "--merchant", help="pubkey of the merchant to listen to events for")
parser.add_argument("-a", "--auction", help="event ID of the auction to listen to bids for (NB: we assume the auction belongs to the specified merchant)")

args = parser.parse_args()

processed_event_ids = set()

if os.path.isfile(PROCESSED_EVENT_IDS_FILENAME):
    with open(PROCESSED_EVENT_IDS_FILENAME, 'r') as f:
        for line in f:
            processed_event_ids.add(line.strip())

logging.info(f"Processed events: {len(processed_event_ids)}")

relays = []

if args.relay:
    relays.append(Relay(args.relay, args, processed_event_ids))
else:
    while True:
        logging.info(f"Connecting to API at {API_BASE_URL}...")
        try:
            response = requests.get(f"{API_BASE_URL}/api/relays").json()
            for relay in response['relays']:
                relays.append(Relay(relay['url'], args, processed_event_ids))
            logging.info(f"Got {len(response['relays'])} relays!")
            break
        except Exception:
            logging.exception(f"Error connecting to API at {API_BASE_URL}! Waiting...")
            time.sleep(1)

asyncio.run(main(relays))
