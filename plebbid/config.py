import os

SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROPAGATE_EXCEPTIONS = False

SECRET_KEY = "TODO"

SQLALCHEMY_DATABASE_URI = 'postgresql://pleb:plebpass@db:5432/plebbid'

BASE_URL = os.environ.get('BASE_URL')
if not BASE_URL:
    VIRTUAL_HOST = os.environ.get('VIRTUAL_HOST')
    if VIRTUAL_HOST:
        BASE_URL = f"https://{VIRTUAL_HOST}"

MOCK_LND = bool(int(os.environ.get("MOCK_LND", 0)))
LND_GRPC = os.environ.get('LND_GRPC')
LND_MACAROON = "/secrets/admin.macaroon"
LND_TLS_CERT = "/secrets/tls.cert"
