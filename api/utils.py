import base58
from base64 import b32encode
import hashlib
import magic
from os import urandom
from pycoin.symbols.btc import network as BTC
from pycoin.symbols.xtn import network as TESTNET
import requests
import semver

def hash_create(length):
    return b32encode(urandom(length)).decode("ascii").replace("=", "")

def guess_ext(data):
    return magic.Magic(extension=True).from_buffer(data).split("/")[0]

def pick_ext(choices):
    for e in choices:
        if e.isalnum() and len(e) <= 5:
            return f".{e}"
    else:
        return ""

def store_image(file_storage, filename, append_hash, original_filename, data):
    if data is None:
        url = original_filename
        response = requests.get(url)
        if response.status_code != 200:
            return None, None
        data = response.content

    sha = hashlib.sha256()
    sha.update(data)
    content_hash = sha.hexdigest()

    ext = pick_ext([guess_ext(data), original_filename.rsplit('.', 1)[-1]])
    filename = f"{filename}_{content_hash}{ext}" if append_hash else f"{filename}{ext}"

    file_storage.upload(data, filename)

    return file_storage.get_url_prefix() + file_storage.get_filename_prefix() + filename, content_hash

def usd2sats(amount: float, btc2usd: float) -> int:
    from main import app
    return int(amount / btc2usd * app.config['SATS_IN_BTC'])

def sats2usd(amount: float, btc2usd: float) -> float:
    from main import app
    return (amount * btc2usd) / app.config['SATS_IN_BTC']

class UnknownKeyTypeError(Exception):
    def __str__(self):
        return f"Unknown key type!"

PUB_PREFIXES = {
    'zpub': '04b24746',
}

def parse_xpub(xpub):
    coin = BTC
    if xpub.lower().startswith('x'):
        xpub_bip32 = BTC.parse.bip32_pub(xpub)
        # Convert XPUB to ZPUB
        decoded_extended_publicKey = base58.b58decode_check(xpub)
        extended_public_key_no_prefix = decoded_extended_publicKey[4:]
        extended_public_key_new_prefix = bytes.fromhex(PUB_PREFIXES['zpub']) + extended_public_key_no_prefix
        zpub = base58.b58encode_check(extended_public_key_new_prefix).decode('UTF-8')
    elif xpub.lower().startswith('z'):
        zpub = xpub
    elif xpub.lower().startswith('v'):
        zpub = xpub
        coin = TESTNET
    else:
        raise UnknownKeyTypeError()

    return coin.parse.bip84_pub(zpub)

def parse_github_tag(t):
    if t.startswith("v"):
        t = t[1:]
    return semver.Version.parse(t)
