import json
import os

RELEASE_VERSION = os.environ.get('RELEASE_VERSION', "")

GITHUB_OWNER = 'PlebeianTech'
GITHUB_REPO = 'plebeian-market'

UPDATE_REQUESTED_FILE = "/state/UPDATE_REQUESTED"

SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROPAGATE_EXCEPTIONS = False

BID_LAST_MINUTE_EXTEND = int(os.environ.get('BID_LAST_MINUTE_EXTEND', 5))

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

AUTO_CONFIGURE_SITE = bool(int(os.environ.get('AUTO_CONFIGURE_SITE', 0)))

API_BASE_URL = os.environ.get('API_BASE_URL')
API_BASE_URL_EXTERNAL = os.environ.get('API_BASE_URL_EXTERNAL') # used to mock S3 in dev mode and have the browser (which is not running in the docker container) hit the mock directly
BIRDWATCHER_BASE_URL = os.environ.get('BIRDWATCHER_BASE_URL')
WWW_BASE_URL = os.environ.get('WWW_BASE_URL')
DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
SITE_NAME = "Plebeian Market"

LNAUTH_EXPIRE_MINUTES = 120
JWT_EXPIRE_DAYS = 420

USER_EMAIL_VERIFICATION = bool(int(os.environ.get('USER_EMAIL_VERIFICATION', 1)))

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

MOCK_S3 = bool(int(os.environ.get('MOCK_S3', 0)))
USE_S3 = bool(int(os.environ.get('USE_S3', 0)))
if USE_S3:
    S3_SECRETS = "/secrets/s3.json"
    S3_ENDPOINT_URL = "https://s3.us-west-004.backblazeb2.com"
    S3_BUCKET = 'plebeian-market'
    S3_FILENAME_PREFIX = os.environ.get('S3_FILENAME_PREFIX', "")
    S3_URL_PREFIX = f"https://f004.backblazeb2.com/file/{S3_BUCKET}/"

SATS_IN_BTC = 100000000

SKIN_IN_THE_GAME_BADGE_ID = 'pm-sitg'

# The "site admin" is the owner of the stall that sells badges (such as Skin in the Game) and receives money for these badges.
# It can be missing, in which case the site can "inherit" badges from another Plebeian Market instance.
SITE_ADMIN_SECRETS = "/secrets/site-admin.json"

# BADGE_DEFINITION_XXX are templates for badges that this site wishes to define - *if* it has its own badges!
# These templates are translated into actual badges (models.Badge) by running `flask configure-site` and published as Nostr badges.
# Sites that wish to inherit badges from other instances rather than sell their own should ignore these badge definitions
# and *not* run "configure-site", in which case they will be presented with an extra configuration page (NewSite.svelte) before the first log in
# and badges will be imported rather than generated from these templates!
BADGE_DEFINITION_TESTER = {
    'badge_id': "pm-tester",
    'name': f"{SITE_NAME} Chief tester",
    'description': f"Helped testing {SITE_NAME}",
    'image_url': f"{WWW_BASE_URL}/badges/tester.png",
}

BADGE_DEFINITION_OG = {
    'badge_id': "pm-og",
    'name': f"{SITE_NAME} OG",
    'description': f"Early {SITE_NAME} user",
    'image_url': f"{WWW_BASE_URL}/badges/og.png",
}

BADGE_DEFINITION_SKIN_IN_THE_GAME = {
    'badge_id': SKIN_IN_THE_GAME_BADGE_ID,
    'name': f"{SITE_NAME} Skin in the Game",
    'description': f"Made a monetary contribution to {SITE_NAME}",
    'image_url': f"{WWW_BASE_URL}/badges/skin-in-the-game.png",
    'price_usd': 0.2 if ENV == 'staging' else 21,
}

# NB: keep in sync with `relayUrlList` under `web/shared/src/lib/nostr/utils.ts`
DEFAULT_RELAYS = ["wss://staging.plebeian.market/relay"] if ENV == 'staging' else [
    "wss://relay.damus.io",
    "wss://relay.nostr.bg",
    "wss://nostr.mom",
    "wss://nos.lol",
    "wss://nostr.bitcoiner.social",
    "wss://nostr-pub.wellorder.net",
    "wss://nostr.wine",
    "wss://eden.nostr.land",
    "wss://relay.orangepill.dev",
    "wss://puravida.nostr.land",
    "wss://relay.nostr.com.au",
    "wss://nostr.inosta.cc",
]

# for sites that do not sell their own badges, they can use this badge - which is essentially the plebeian.market badge!
# TODO: remove this and use the /badges API endpoint of the plebeian.market instance to obtain the information! 
DEFAULT_BADGE_SKIN_IN_THE_GAME = {
    'badge_id': 'pm-sitg',
    'owner_public_key': "76cc29acb8008c68b105cf655d34de0b1f7bc0215eaae6bbc83173d6d3f7b987",
    'name': "Plebeian Market Skin in the Game",
    'description': "Made a monetary contribution to Plebeian Market",
    'image_hash': "4c87ec576a57a9eafa2d35fc3535a45683dc9aa2ae02af8b85e1b2d8addcf1c2",
    'nostr_event_id': "4a8891b6e8b65fe93d749600a2488df1a7c0c7e43a4b6fc46c4a145b03518506",
    'stall_id': "39863a931522a83e4ba2872c8a0d2d2366a662b344f4a31ca1027d6c8c492cc1",
    'listing_uuid': "04cafe6e-d1f0-4cce-9d0d-7af1a0f71953",
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
