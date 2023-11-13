#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/do.sh prod build && $DIR/do.sh prod down && docker volume rm plebeian-market_buyer-app-static-content && $DIR/do.sh prod up -d
