from aiofile import async_open
import aiohttp
from aiohttp import web
import argparse
from arsenic import get_session
from arsenic.browsers import Firefox
from arsenic.services import Geckodriver
import asyncio
import bech32
from bs4 import BeautifulSoup
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
import websockets

BIRDWATCHER_PORT = 6000

ENV = os.environ.get('ENV')

API_BASE_URL = os.environ.get('API_BASE_URL')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILENAME = os.environ.get('LOG_FILENAME', "pm.log")
PROCESSED_EVENT_IDS_FILENAME = os.environ.get('PROCESSED_EVENT_IDS_FILENAME')
VERIFIED_EXTERNAL_IDENTITIES_FILENAME = os.environ.get('VERIFIED_EXTERNAL_IDENTITIES_FILENAME')
GECKODRIVER_BINARY = os.environ.get('GECKODRIVER_BINARY')

PERMANENT_API_ERROR_STATI = [400, 403, 404]
RECOVERABLE_API_ERROR_STATI = [500]

dictConfig({
    'version': 1,
    'formatters': {'default': {'format': "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}},
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILENAME,
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10,
        },
    },
    'root': {'level': LOG_LEVEL, 'handlers': ['default', 'info_rotating_file_handler']},
})

def pk2npub(pk):
    return bech32.bech32_encode('npub', bech32.convertbits(bytes.fromhex(pk), 8, 5))

class EventKind(IntEnum):
    METADATA = 0
    DM = 4
    BADGE_AWARD = 8
    STALL = 30017
    AUCTION = 30020
    BID = 1021

class Relay:
    def __init__(self, url, args, processed_event_ids, event_ids_being_processed):
        self.url = url
        self.args = args
        self.processed_event_ids = processed_event_ids
        self.event_ids_being_processed = event_ids_being_processed

        self.ws = None

        self.events_to_process = asyncio.queues.Queue()

        self.subscribed_auction_event_ids = set()
        self.subscribed_merchant_pubkeys = set()

        self.bid_subscription_id = None
        self.dm_subscription_id = None

        self.auction_owners = {} # event ID to pubkey

        self.active_queries: dict[str, asyncio.Event] = {}
        self.query_results: dict[str, list[dict]] = {}

    async def check_ours(self, event, subscribe_cb):
        async def do_get(session, url):
            async with session.get(url) as response:
                if response.status == 404:
                    logging.debug(f"Not our merchant {event['pubkey']}...")
                elif response.status == 200:
                    await subscribe_cb(**event)
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(do_get(session, f"{API_BASE_URL}/api/merchants/{event['pubkey']}"))

    async def get_our_merchants(self, subscribe_cb):
        async def do_get(session, url):
            async with session.get(url) as response:
                merchants_response = await response.json()
                merchant_pks = [m['public_key'] for m in merchants_response]
                await subscribe_cb(merchant_pks)
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(do_get(session, f"{API_BASE_URL}/api/merchants"))

    async def post_dm(self, merchant_pubkey, dm_event):
        async def do_post(session, url, json):
            async with session.post(url, json=json) as response:
                logging.debug(f"POST to merchant {merchant_pubkey}: {dm_event}")
                response_json = None
                try:
                    response_json = await response.json()
                    logging.debug(f"POST responded with {response_json}!")
                except Exception:
                    response_text = await response.text()
                    logging.debug(f"POST responded with {response_text}!")
                if response.status == 200:
                    logging.info(f"Forwarded message to merchant {merchant_pubkey}.")
                elif response.status == 409:
                    logging.info(f"Order already exists at {merchant_pubkey}.")
                elif response.status in PERMANENT_API_ERROR_STATI or response.status in RECOVERABLE_API_ERROR_STATI:
                    logging.error(f"Error posting to merchant {merchant_pubkey}: {response.status}; message={response_json.get('message') if response_json else None}.")
                else:
                    logging.error(f"Unknown status when posting to merchant {merchant_pubkey}: {response.status}.")
                return response.status
        async with aiohttp.ClientSession() as session:
            task = asyncio.create_task(do_post(session, f"{API_BASE_URL}/api/merchants/{merchant_pubkey}/messages", dm_event))
            await task
            return task.result()

    async def post_bid(self, auction_event_id, bid_event):
        merchant_pubkey = self.auction_owners[auction_event_id]
        async def do_post(session, url, json):
            async with session.post(url, json=json) as response:
                logging.debug(f"POST to auction {auction_event_id} of merchant {merchant_pubkey}: {bid_event}")
                if response.status == 200:
                    logging.info(f"Forwarded bid to auction {auction_event_id} of merchant {merchant_pubkey}.")
                elif response.status in PERMANENT_API_ERROR_STATI or response.status in RECOVERABLE_API_ERROR_STATI:
                    logging.error(f"Error posting bid to auction {auction_event_id} of merchant {merchant_pubkey}: {response.status}.")
                else:
                    logging.error(f"Unknown status when posting bid to auction {auction_event_id} of merchant {merchant_pubkey}: {response.status}.")
                try:
                    response_json = await response.json()
                    logging.debug(f"POST responded with {response_json}!")
                except Exception:
                    response_text = await response.text()
                    logging.debug(f"POST responded with {response_text}!")
                return response.status
        async with aiohttp.ClientSession() as session:
            task = asyncio.create_task(do_post(session, f"{API_BASE_URL}/api/merchants/{merchant_pubkey}/auctions/{auction_event_id}/bids", bid_event))
            await task
            return task.result()

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
            if self.dm_subscription_id is not None:
                logging.info(f"({self.url}) Closing subscription for DMs of {len(self.subscribed_merchant_pubkeys)} merchants: {self.dm_subscription_id}...")
                await self.ws.send(json.dumps(['CLOSE', self.dm_subscription_id]))
            self.subscribed_merchant_pubkeys.add(pubkey)
            self.dm_subscription_id = os.urandom(10).hex()
            logging.info(f"({self.url}) Subscribing to DMs of {len(self.subscribed_merchant_pubkeys)} merchants: {self.dm_subscription_id}...")
            await self.ws.send(json.dumps(['REQ', self.dm_subscription_id, {"#p": list(self.subscribed_merchant_pubkeys), 'kinds': [EventKind.DM]}]))
            return self.dm_subscription_id

    async def subscribe_dm_all(self, pubkeys):
        if self.dm_subscription_id is not None:
            logging.info(f"({self.url}) Closing subscription for DMs of {len(self.subscribed_merchant_pubkeys)} merchants: {self.dm_subscription_id}...")
            await self.ws.send(json.dumps(['CLOSE', self.dm_subscription_id]))
        self.subscribed_merchant_pubkeys |= set(pubkeys)
        self.dm_subscription_id = os.urandom(10).hex()
        logging.info(f"({self.url}) Subscribing to DMs of {len(self.subscribed_merchant_pubkeys)} merchants: {self.dm_subscription_id}...")
        await self.ws.send(json.dumps(['REQ', self.dm_subscription_id, {"#p": list(self.subscribed_merchant_pubkeys), 'kinds': [EventKind.DM]}]))
        return self.dm_subscription_id

    async def subscribe_bids(self, pubkey, id, **_):
        if id not in self.subscribed_auction_event_ids:
            if self.bid_subscription_id is not None:
                logging.info(f"({self.url}) Closing subscription for bids of {len(self.subscribed_auction_event_ids)} auctions: {self.bid_subscription_id}...")
                await self.ws.send(json.dumps(['CLOSE', self.bid_subscription_id]))
            self.subscribed_auction_event_ids.add(id)
            assert id not in self.auction_owners
            self.auction_owners[id] = pubkey
            self.bid_subscription_id = os.urandom(10).hex()
            logging.info(f"({self.url}) Subscribing to bids of {len(self.subscribed_auction_event_ids)} auctions: {self.bid_subscription_id}...")
            await self.ws.send(json.dumps(['REQ', self.bid_subscription_id, {"#e": list(self.subscribed_auction_event_ids), 'kinds': [EventKind.BID]}]))
            return self.bid_subscription_id

    async def send_event(self, event):
        if self.ws is not None:
            logging.info(f"({self.url}) Sending event {event['id']}...")
            await self.ws.send(json.dumps(['EVENT', event]))

    async def send_query(self, subscription_id: str, filters: dict):
        if self.ws is not None:
            logging.info(f"({self.url}) Sending query {filters}...")
            self.active_queries[subscription_id] = asyncio.Event()
            self.query_results[subscription_id] = []
            await self.ws.send(json.dumps(['REQ', subscription_id, filters]))

    async def process_event(self, event):
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
                merchant_pubkey = [t for t in event['tags'] if t[0] == 'p'][0][1]
                logging.info(f"({self.url}) POSTing DM event to API: {event['id']}")
                post_status = await self.post_dm(merchant_pubkey, event)
                if post_status not in RECOVERABLE_API_ERROR_STATI:
                    self.processed_event_ids.add(event['id'])
                    if PROCESSED_EVENT_IDS_FILENAME:
                        async with async_open(PROCESSED_EVENT_IDS_FILENAME, 'a') as f:
                            await f.write(f"{event['id']}\n")
            case EventKind.BID:
                auction_event_id = [t for t in event['tags'] if t[0] == 'e'][0][1]
                logging.info(f"({self.url}) POSTing bid event to API: {event['id']}")
                post_status = await self.post_bid(auction_event_id, event)
                if post_status not in RECOVERABLE_API_ERROR_STATI:
                    self.processed_event_ids.add(event['id'])
                    if PROCESSED_EVENT_IDS_FILENAME:
                        async with async_open(PROCESSED_EVENT_IDS_FILENAME, 'a') as f:
                            await f.write(f"{event['id']}\n")

    async def listen(self):
        while True:
            if self.ws is None:
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
                else:
                    await self.get_our_merchants(self.subscribe_dm_all)
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
                    match message[0]:
                        case 'NOTICE':
                            logging.info(f"({self.url}) NOTICE {message[1]}...")
                        case 'EOSE':
                            subscription_id = message[1]
                            if subscription_id in self.active_queries:
                                logging.info(f"({self.url}) Closing subscription {subscription_id}...")
                                await self.ws.send(json.dumps(['CLOSE', subscription_id]))
                                self.active_queries[subscription_id].set()
                        case 'EVENT':
                            subscription_id = message[1]
                            event = message[2]
                            if subscription_id in self.active_queries:
                                logging.info(f"({self.url}) Got EVENT as a reply for query {subscription_id}.")
                                self.query_results[subscription_id].append(event)
                            else:
                                logging.info(f"({self.url}) Got EVENT {event}. Adding to queue...")
                                self.events_to_process.put_nowait(event)
            except Exception:
                self.ws = None
                logging.exception(f"({self.url}) Connection closed.")
                await asyncio.sleep(10)

    async def process_events(self):
        while True:
            if self.events_to_process.empty():
                await asyncio.sleep(0.1)
                continue
            event = await self.events_to_process.get()
            if event['id'] in self.event_ids_being_processed:
                logging.info(f"({self.url}) Skipping event currently being processed: {event['id']}!")
            elif event['id'] in self.processed_event_ids:
                logging.info(f"({self.url}) Skipping event already processed: {event['id']}!")
            else:
                logging.info(f"({self.url}) Processing event {event['id']}...")
                self.event_ids_being_processed.add(event['id'])
                try:
                    await asyncio.create_task(self.process_event(event))
                finally:
                    self.event_ids_being_processed.remove(event['id'])

async def get_url_aiohttp(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.url, await response.text()

async def get_url_arsenic(url):
    service = Geckodriver(binary=GECKODRIVER_BINARY) if GECKODRIVER_BINARY else Geckodriver()
    browser = Firefox(**{'moz:firefoxOptions': {'args': ['-headless']}})
    async with get_session(service, browser) as session:
        await session.get(url)
        return await session.get_url(), await session.get_page_source()

def twitter_verifier(url, txt, npub, claimed_id):
    # NB: https://twitter.com/saylor/status/1701877505437675910 redirects to https://twitter.com/ibz/status/1701877505437675910
    # so we need to check the final URL in addition to checking that the tweet contains the pubkey
    id_ok = url.startswith(f"https://twitter.com/{claimed_id}/")
    key_ok = npub in txt

    return id_ok and key_ok

def telegram_verifier(_url, txt, npub, claimed_id):
    bs = BeautifulSoup(txt, features="html.parser")
    try:
        id_ok = bs.select("a.tgme_widget_message_author_name")[0]['href'] == f"https://t.me/{claimed_id}"
    except (IndexError, KeyError):
        return False
    try:
        key_ok = npub in bs.select("div.tgme_widget_message_text")[0].text
    except IndexError:
        return False

    return id_ok and key_ok

async def verify_external_identity(pk, external_identity, proof):
    service, claimed_id = external_identity.split(":")
    match service:
        case 'twitter':
            getter, url, verifier = get_url_arsenic, f"https://twitter.com/{claimed_id}/status/{proof}", twitter_verifier
        case 'github':
            getter, url, verifier = get_url_aiohttp, f"https://gist.githubusercontent.com/{claimed_id}/{proof}/raw/gistfile1.txt", lambda _url, txt, npub, _: npub in txt
        case 'telegram':
            getter, url, verifier = get_url_aiohttp, f"https://t.me/{proof}?embed=1&mode=tme", telegram_verifier
        case _:
            return pk, external_identity, False

    try:
        logging.info(f"Getting {url}...")
        response_url, response_text = await getter(url)
        logging.info(f"Got {url} as {response_url}: {len(response_text)} bytes!")
    except:
        logging.exception("Error verifying external identity.")
        return pk, external_identity, False

    return pk, external_identity, verifier(response_url, response_text, pk2npub(pk), claimed_id)

async def main(relays: list[Relay]):
    all_tasks = []
    for relay in relays:
        all_tasks.append(asyncio.create_task(relay.listen()))
        all_tasks.append(asyncio.create_task(relay.process_events()))

    app = web.Application()
    routes = web.RouteTableDef()

    # cache of verified NIP-39 identities
    verified_external_identities = {}
    if VERIFIED_EXTERNAL_IDENTITIES_FILENAME:
        if os.path.isfile(VERIFIED_EXTERNAL_IDENTITIES_FILENAME):
            with open(VERIFIED_EXTERNAL_IDENTITIES_FILENAME, 'r') as f:
                for line in f:
                    pk, external_identity = line.strip().split(" ", 1)
                    verified_external_identities.setdefault(pk, set()).add(external_identity)
        logging.info(f"Verified external identities for: {len(verified_external_identities)} keys.")
    else:
        logging.warning("Verified external identities will not be persisted!")

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

    @routes.post("/query")
    async def query(request):
        query_json = await request.json()
        filters = None
        if query_json.get('metadata') and query_json.get('author'):
            filters = {'kinds': [EventKind.METADATA], 'authors': [query_json['author']]}
        if query_json.get('badge_award') and query_json.get('author') and query_json.get('awardee'):
            filters = {'kinds': [EventKind.BADGE_AWARD], 'authors': [query_json['author']], '#p': [query_json['awardee']]}
        if filters is None:
            raise web.HTTPBadRequest()

        subscription_id = os.urandom(10).hex()

        async def send_query():
            for relay in relays:
                try:
                    await relay.send_query(subscription_id, filters)
                except Exception:
                    logging.exception(f"Error sending query to {relay.url}!")

        async def collect_query_results():
            query_results = {}
            for relay in relays:
                if subscription_id in relay.active_queries:
                    try:
                        await asyncio.wait_for(relay.active_queries[subscription_id].wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        logging.error(f"Relay {relay.url} did not finish the reply for {subscription_id} on time!")

                    logging.info(f"Got {len(relay.query_results[subscription_id])} results from {relay.url}!")

                    for event in relay.query_results[subscription_id]:
                        query_results[event['id']] = event # NB: if we get the same event from multiple relays, we only store it once!
                    del relay.active_queries[subscription_id]
                    del relay.query_results[subscription_id]
            return query_results

        await asyncio.create_task(send_query())

        await asyncio.sleep(0.1) # give the query a chance to execute!

        query_results_task = asyncio.create_task(collect_query_results())
        await query_results_task
        query_results = query_results_task.result()

        # NB: for "metadata" events, we also validate the external identities here...

        seen_identities = set()
        verified_identities = []
        verifying_identities = []

        for event in query_results.values():
            if event['kind'] == EventKind.METADATA:
                for tag in event['tags']:
                    if tag[0] == 'i':
                        external_identity = tag[1]
                        if external_identity in seen_identities:
                            continue
                        seen_identities.add(external_identity)
                        external_identity_proof = tag[2]
                        if external_identity in verified_external_identities.get(event['pubkey'], []):
                            logging.info(f"Cached external identity verification for {event['pubkey']}: {external_identity}.")
                            verified_identities.append(external_identity)
                        else:
                            logging.info(f"Verifying external identity for {event['pubkey']}: {external_identity}.")
                            verifying_identities.append(await verify_external_identity(event['pubkey'], external_identity, external_identity_proof))

        for pk, external_identity, verification_result in verifying_identities:
            if verification_result:
                verified_external_identities.setdefault(pk, set()).add(external_identity)
                if VERIFIED_EXTERNAL_IDENTITIES_FILENAME:
                    async with async_open(VERIFIED_EXTERNAL_IDENTITIES_FILENAME, 'a') as f:
                        await f.write(f"{pk} {external_identity}\n")
                verified_identities.append(external_identity)

        # NB: we return *all* events because this "query" endpoint is supposed to be as dumb as possible...
        # ... it is simply a way to hit the relays and return the results, without much hidden logic ...
        # In the case of metadata events, for example, the caller should only pick the latest event,
        # but that would not be the case if we later - for example - give this endpoint the ability to query TEXT events!

        return web.json_response({'events': list(query_results.values()), 'verified_identities': verified_identities})

    @routes.post("/relays")
    async def post_relay(request):
        relay_json = await request.json()
        logging.info(f"Adding new relay: {relay_json['url']}!")
        try:
            relay = Relay(relay_json['url'], args, processed_event_ids, event_ids_being_processed)
            relays.append(relay)
            all_tasks.append(asyncio.create_task(relay.listen()))
            all_tasks.append(asyncio.create_task(relay.process_events()))
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
event_ids_being_processed = set()

if PROCESSED_EVENT_IDS_FILENAME:
    if os.path.isfile(PROCESSED_EVENT_IDS_FILENAME):
        with open(PROCESSED_EVENT_IDS_FILENAME, 'r') as f:
            for line in f:
                processed_event_ids.add(line.strip())
    logging.info(f"Processed events: {len(processed_event_ids)}")
else:
    logging.warning("Processed event IDs will not be persisted!")

logging.warning("No API_BASE_URL to connect to!")

relays: list[Relay] = []

if args.relay:
    relays.append(Relay(args.relay, args, processed_event_ids, event_ids_being_processed))
else:
    if API_BASE_URL:
        while True:
            logging.info(f"Connecting to API at {API_BASE_URL}...")
            try:
                response = requests.get(f"{API_BASE_URL}/api/relays").json()
                for relay in response['relays']:
                    relays.append(Relay(relay['url'], args, processed_event_ids, event_ids_being_processed))
                logging.info(f"Got {len(response['relays'])} relays!")
                break
            except Exception:
                logging.exception(f"Error connecting to API at {API_BASE_URL}! Waiting...")
                time.sleep(1)
    else:
        logging.error("No relays. Nothing to do. Pass a --relay or use API_BASE_URL to have BirdWatcher fetch relays to connect to!")
        sys.exit(1)

asyncio.run(main(relays))
