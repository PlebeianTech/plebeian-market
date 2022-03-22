import os

BASE_URL = os.environ.get('BASE_URL')
if not BASE_URL:
    VIRTUAL_HOST = os.environ.get('VIRTUAL_HOST')
    if VIRTUAL_HOST:
        BASE_URL = f"https://{VIRTUAL_HOST}"

SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROPAGATE_EXCEPTIONS = False

SECRET_KEY = "TODO"

SQLALCHEMY_DATABASE_URI = 'postgresql://pleb:plebpass@db:5432/plebbid'
