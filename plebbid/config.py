import os

BASE_URL = "https://plebbid.21art.gallery"

SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROPAGATE_EXCEPTIONS = False

SECRET_KEY = "TODO"

SQLALCHEMY_DATABASE_URI = 'postgresql://pleb:plebpass@db:5432/plebbid'
