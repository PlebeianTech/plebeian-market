import aiohttp
import asyncio
from dataclasses import dataclass
from enum import IntEnum
import json
import logging
from logging.config import dictConfig
from nostr.key import PrivateKey
import os
import requests
import sys
import time
from typing import List
import websockets

API_BASE_URL = os.environ.get('API_BASE_URL')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

dictConfig({
    'version': 1,
    'formatters': {'default': {'format': "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}},
    'handlers': {'default': {'class': 'logging.StreamHandler', 'formatter': 'default'}},
    'root': {'level': LOG_LEVEL, 'handlers': ['default']},
})

class EventKind(IntEnum):
    DM = 4
    STALL = 30017

@dataclass
class Relay:
    url: str
    stall_pubkeys: List[str]

    async def check_stall(self, stall_pubkey):
        async def do_get(session, url):
            async with session.get(url) as response:
                if response.status == 404:
                    logging.debug(f"Not our stall {stall_pubkey}...")
                elif response.status == 200:
                    if stall_pubkey not in self.stall_pubkeys:
                        logging.info(f"Found stall {stall_pubkey}!")
                        self.stall_pubkeys.append(stall_pubkey)
                        await self.subscribe_dm(stall_pubkey)
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(do_get(session, f"{API_BASE_URL}/api/stalls/{stall_pubkey}"))

    async def post_dm(self, stall_pubkey, dm_event):
        async def do_post(session, url, json):
            async with session.post(url, json=json) as response:
                logging.debug(f"POST to stall {stall_pubkey}: {dm_event}")
                if response.status == 200:
                    logging.info(f"Forwarded message to stall {stall_pubkey}.")
                elif response.status == 409:
                    logging.info(f"Order already exists at {stall_pubkey}.")
                elif response.status == 500:
                    logging.error(f"Error posting to stall {stall_pubkey}.")
                try:
                    response_json = await response.json()
                    logging.debug(f"POST responded with {response_json}!")
                except Exception:
                    response_text = await response.text()
                    logging.debug(f"POST responded with {response_text}!")
        async with aiohttp.ClientSession() as session:
            await asyncio.create_task(do_post(session, f"{API_BASE_URL}/api/stalls/{stall_pubkey}/events", dm_event))

    async def subscribe_stall(self):
        logging.info(f"({self.url}) Subscribing for stall events...")
        subscription_id = os.urandom(10).hex()
        await self.ws.send(json.dumps(['REQ', subscription_id, {'kinds': [EventKind.STALL]}]))
        return subscription_id

    async def subscribe_dm(self, pubkey):
        logging.info(f"({self.url}) Subscribing DM for {pubkey}...")
        subscription_id = os.urandom(10).hex()
        await self.ws.send(json.dumps(['REQ', subscription_id, {"#p": [pubkey], 'kinds': [EventKind.DM]}]))
        return subscription_id

    async def listen(self):
        while True:
            logging.info(f"({self.url}) Connecting...")
            try:
                self.ws = await websockets.connect(self.url)
            except Exception:
                logging.exception(f"({self.url}) Cannot connect.")
                return

            try:
                stall_subscription_id = None
                if self.stall_pubkeys:
                    # if we got some pubkeys to start with, just go with those...
                    for stall_pubkey in self.stall_pubkeys:
                        await self.subscribe_dm(stall_pubkey)
                else:
                    # ... otherwise we need to discover the stalls
                    stall_subscription_id = await self.subscribe_stall()
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
                            case EventKind.STALL:
                                await self.check_stall(event['pubkey'])
                            case EventKind.DM:
                                stall_pubkey = [t for t in event['tags'] if t[0] == 'p'][0][1]
                                await self.post_dm(stall_pubkey, event)
            except Exception:
                logging.error(f"({self.url}) Connection closed.")
                await asyncio.sleep(10)

async def main():
    for task in asyncio.as_completed([asyncio.create_task(relay.listen()) for relay in relays]):
        await task

stall_pubkeys = []

if len(sys.argv) > 2:
    stall_pubkeys.append(sys.argv[2])

relays = []

if len(sys.argv) > 1:
    relays.append(Relay(sys.argv[1], stall_pubkeys))

while len(relays) == 0:
    logging.info(f"Connecting to API at {API_BASE_URL}...")
    response = requests.get(f"{API_BASE_URL}/api/relays")
    relay_urls = [r['url'] for r in response.json()['relays']]
    logging.info(f"Got {len(relay_urls)} relays!")
    for url in relay_urls:
        relays.append(Relay(url, stall_pubkeys))
    if len(relays) == 0:
        time.sleep(10)

asyncio.run(main())
