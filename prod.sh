#!/bin/sh

export BUILD_ID=$(LC_ALL=C tr -dc A-Za-z0-9 < /dev/urandom | head -c 6)
./do.sh prod build && ./do.sh prod down && ./do.sh prod up -d
