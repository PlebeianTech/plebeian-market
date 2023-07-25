import json
import os

SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROPAGATE_EXCEPTIONS = False

BID_LAST_MINUTE_EXTEND = int(os.environ.get('BID_LAST_MINUTE_EXTEND', 5))
BID_ALWAYS_EXTEND_BY_MINUTES = int(os.environ.get('BID_ALWAYS_EXTEND_BY_MINUTES', 0))

if DEBUG:
    SECRET_KEY = "DEBUG_SECRET_KEY_IS_NOT_REALLY_SECRET"
else:
    with open("/secrets/secret_key") as f:
        SECRET_KEY = f.read()

DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
if DB_USERNAME is None or DB_PASSWORD is None:
    # NB: we check for None, not for ""
    # for the tests we set these to "", so no secrets file is needed, but that will result in an invalid SQLALCHEMY_DATABASE_URI
    # which is fine, since the tests should not access the database directly!
    with open("/secrets/db.json") as f:
        db = json.load(f)
        if DB_USERNAME is None:
            DB_USERNAME = db['USERNAME']
        if DB_PASSWORD is None:
            DB_PASSWORD = db['PASSWORD']

SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@db:5432/market"

if bool(int(os.environ.get("SQLALCHEMY_DISABLE_POOLING", 0))):
    from sqlalchemy.pool import NullPool
    SQLALCHEMY_ENGINE_OPTIONS = {'poolclass': NullPool}

ENV = os.environ.get('ENV')

API_BASE_URL = os.environ.get('API_BASE_URL')
API_BASE_URL_EXTERNAL = os.environ.get('API_BASE_URL_EXTERNAL') # used to mock S3 in dev mode and have the browser (which is not running in the docker container) hit the mock directly
BIRDWATCHER_BASE_URL = os.environ.get('BIRDWATCHER_BASE_URL')
WWW_BASE_URL = os.environ.get('WWW_BASE_URL')
DOMAIN_NAME = "plebeian.market"

LNAUTH_EXPIRE_MINUTES = 120
JWT_EXPIRE_DAYS = 420

MOCK_BTC = bool(int(os.environ.get("MOCK_BTC", 0)))

MOCK_LND = bool(int(os.environ.get("MOCK_LND", 0)))
LND_GRPC = os.environ.get('LND_GRPC')
LND_MACAROON = "/secrets/admin.macaroon"
LND_TLS_CERT = "/secrets/tls.cert"
LND_BID_INVOICE_AMOUNT = 21 if ENV != 'staging' else 1
LND_BID_INVOICE_EXPIRY = 10 * 60 # 10 minutes
LND_CONTRIBUTION_INVOICE_EXPIRY_AUCTION = 3 * 24 * 60 * 60 # 3 days
LND_CONTRIBUTION_INVOICE_EXPIRY_LISTING = 30 * 60 # 30 minutes

MINIMUM_CONTRIBUTION_AMOUNT = 21
CONTRIBUTION_PERCENT_DEFAULT = 5.0 # NB: must be in sync with the value in V4V.svelte

MOCK_TWITTER = bool(int(os.environ.get("MOCK_TWITTER", 0)))
TWITTER_USER_MIN_AGE_DAYS = 210
TWITTER_USER_MIN_AGE_DAYS_WHITELIST = ["ghostofmtc", "civilbtcsaver", "shoresychirpstv"]
TWITTER_SECRETS = "/secrets/twitter.json"
TWITTER_USER = "PlebeianMarket"

MOCK_NOSTR = bool(int(os.environ.get("MOCK_NOSTR", 0)))
NOSTR_SECRETS = "/secrets/nostr.json"
DEFAULT_NOSTR_RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.nostr.bg",
    "wss://nostr.mom",
    "wss://nos.lol",
    "wss://nostr.bitcoiner.social",
    "wss://nostr-pub.wellorder.net",
    "wss://nostr.wine",
    "wss://eden.nostr.land",
    "wss://relay.orangepill.dev",
    "wss://no.str.cr",
    "wss://puravida.nostr.land",
    "wss://relay.nostr.com.au",
    "wss://nostr.inosta.cc",
]

MOCK_S3 = bool(int(os.environ.get("MOCK_S3", 0)))
S3_SECRETS = "/secrets/s3.json"
S3_ENDPOINT_URL = "https://s3.us-west-004.backblazeb2.com"
S3_BUCKET = 'plebeian-market'
S3_FILENAME_PREFIX = os.environ.get('S3_FILENAME_PREFIX', "")
S3_URL_PREFIX = f"https://f004.backblazeb2.com/file/{S3_BUCKET}/"

MODERATOR_USER_IDS = [(int(i) if i.isnumeric() else i) for i in os.environ.get('MODERATOR_USER_IDS', "1").split(',')]

SATS_IN_BTC = 100000000

SKIN_IN_THE_GAME_THRESHOLDS = [
    {'bid_amount_usd': 1000.0, 'required_amount_spent_usd': 50.0},
]
