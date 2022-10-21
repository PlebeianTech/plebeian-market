from base64 import b32encode
import hashlib
import magic
import requests
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

def store_image(s3, filename, append_hash, original_filename, data):
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

    s3.upload(data, filename)

    return s3.get_url_prefix() + s3.get_filename_prefix() + filename, content_hash

def usd2sats(amount, btc2usd):
    from main import app
    return int(amount / btc2usd * app.config['SATS_IN_BTC'])

def sats2usd(amount, btc2usd):
    from main import app
    return (amount * btc2usd) / app.config['SATS_IN_BTC']
