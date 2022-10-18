from base64 import b32encode
import magic
from os import urandom

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

def usd2sats(amount, btc2usd):
    from main import app
    return int(amount / btc2usd * app.config['SATS_IN_BTC'])

def sats2usd(amount, btc2usd):
    from main import app
    return (amount * btc2usd) / app.config['SATS_IN_BTC']
