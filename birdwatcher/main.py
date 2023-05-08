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
import time
import websockets

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

    async def subscribe_stall(self):
        logging.info(f"({self.url}) Subscribing for stall events...")
        await self.ws.send(json.dumps(['REQ', os.urandom(10).hex(), {'kinds': [EventKind.STALL]}]))

    async def subscribe_dm(self, pubkey):
        logging.info(f"({self.url}) Subscribing DM for {pubkey}...")
        await self.ws.send(json.dumps(['REQ', os.urandom(10).hex(), {"#p": [pubkey], 'kinds': [EventKind.DM]}]))

    async def listen(self):
        logging.info(f"({self.url}) Connecting...")
        try:
            self.ws = await websockets.connect(self.url)
        except:
            logging.exception(f"({self.url}) Cannot connect.")
            return

        await self.subscribe_stall()

        async for message in self.ws:
            logging.debug(f"({self.url}) Received: {message}!")
            message = json.loads(message)
            if message[0] == 'EVENT':
                match message[2]['kind']:
                    case EventKind.STALL:
                        await self.subscribe_dm(message[2]['pubkey'])
                    case EventKind.DM:
                        stall_pubkey = [t for t in message[2]['tags'] if t[0] == 'p'][0][1]
                        await post_dm(stall_pubkey, message[2])

relays = []

API_BASE_URL = os.environ.get('API_BASE_URL')

async def post_dm(stall_pubkey, dm_event):
    async def do_post(session, url, data):
        async with session.post(url, data=data) as response:
            logging.debug(f"POST to stall {stall_pubkey}: {dm_event}")
            if response.status == 200:
                logging.info(f"Forwarded message to stall {stall_pubkey}.")
            elif response.status == 500:
                logging.error(f"Error posting to stall {stall_pubkey}.")
            try:
                response_json = await response.json()
                logging.debug(f"POST responded with {response_json}!")
            except:
                response_text = await response.text()
                logging.debug(f"POST responded with {response_text}!")
    async with aiohttp.ClientSession() as session:
        await asyncio.create_task(do_post(session, f"{API_BASE_URL}/api/stalls/{stall_pubkey}/events", dm_event))

while len(relays) == 0:
    logging.info(f"Connecting to API at {API_BASE_URL}...")
    response = requests.get(f"{API_BASE_URL}/api/relays")
    relay_urls = [r['url'] for r in response.json()['relays']]
    logging.info(f"Got {len(relay_urls)} relays!")
    for url in relay_urls:
        relays.append(Relay(url))
    if len(relays) == 0:
        time.sleep(10)

async def main():
    for task in asyncio.as_completed([asyncio.create_task(relay.listen()) for relay in relays]):
        await task

asyncio.run(main())
