import json
import os

SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROPAGATE_EXCEPTIONS = False

BID_LAST_MINUTE_EXTEND = int(os.environ.get('BID_LAST_MINUTE_EXTEND', 5))
BID_REQUIRED_VERIFIED_IDENTITIES_COUNT = 2

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

APP = os.environ.get('APP')
ENV = os.environ.get('ENV')

API_BASE_URL = os.environ.get('API_BASE_URL')
API_BASE_URL_EXTERNAL = os.environ.get('API_BASE_URL_EXTERNAL') # used to mock S3 in dev mode and have the browser (which is not running in the docker container) hit the mock directly
BIRDWATCHER_BASE_URL = os.environ.get('BIRDWATCHER_BASE_URL')
WWW_BASE_URL = os.environ.get('WWW_BASE_URL')
DOMAIN_NAME = "plebeian.market"
SITE_NAME = "Plebeian Market"

LNAUTH_EXPIRE_MINUTES = 120
JWT_EXPIRE_DAYS = 420

MOCK_MAIL = bool(int(os.environ.get('MOCK_MAIL', 0)))
if not MOCK_MAIL:
    with open("/secrets/mail.json") as f:
        MAIL_SECRETS = json.load(f)
        MAIL_SERVER = MAIL_SECRETS['server']
        MAIL_USERNAME = MAIL_SECRETS['username']
        MAIL_PASSWORD = MAIL_SECRETS['password']
        MAIL_DEFAULT_SENDER = MAIL_SECRETS['default_sender']
        MAIL_USE_TLS = True
else:
    MAIL_SERVER = MAIL_USERNAME = MAIL_PASSWORD = MAIL_DEFAULT_SENDER = None

MOCK_BTC = bool(int(os.environ.get('MOCK_BTC', 0)))

MINIMUM_CONTRIBUTION_AMOUNT = 21
CONTRIBUTION_PERCENT_DEFAULT = 5.0 # NB: must be in sync with the value in V4V.svelte

MOCK_NOSTR = bool(int(os.environ.get("MOCK_NOSTR", 0)))
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

MOCK_S3 = bool(int(os.environ.get('MOCK_S3', 0)))
S3_SECRETS = "/secrets/s3.json"
S3_ENDPOINT_URL = "https://s3.us-west-004.backblazeb2.com"
S3_BUCKET = 'plebeian-market'
S3_FILENAME_PREFIX = os.environ.get('S3_FILENAME_PREFIX', "")
S3_URL_PREFIX = f"https://f004.backblazeb2.com/file/{S3_BUCKET}/"

SATS_IN_BTC = 100000000

SITE_ADMIN_SECRETS = "/secrets/site-admin.json"

BADGE_DEFINITION_TESTER = {
    'badge_id': "pm-tester",
    'name': f"{SITE_NAME} Chief tester",
    'description': f"Helped testing {SITE_NAME}",
    'image_url': f"{WWW_BASE_URL}/badges/tester.png",
}

BADGE_DEFINITION_SKIN_IN_THE_GAME = {
    'badge_id': "pm-sitg",
    'name': f"{SITE_NAME} Skin in the Game",
    'description': f"Made a monetary contribution to {SITE_NAME}",
    'image_url': f"{WWW_BASE_URL}/badges/skin-in-the-game.png",
    'price_usd': 0.21 if ENV == 'staging' else 21,
}

LNDHUB_URL = os.environ.get('LNDHUB_URL')
LNDHUB_USER = os.environ.get('LNDHUB_USER')
LNDHUB_PASSWORD = os.environ.get('LNDHUB_PASSWORD')

MOCK_LNDHUB = bool(int(os.environ.get('MOCK_LNDHUB', 0)))
if not MOCK_LNDHUB:
    with open("/secrets/lndhub.json") as f:
        db = json.load(f)
        if LNDHUB_USER is None:
            LNDHUB_USER = db['LNDHUB_USER']
        if LNDHUB_PASSWORD is None:
            LNDHUB_PASSWORD = db['LNDHUB_PASSWORD']
