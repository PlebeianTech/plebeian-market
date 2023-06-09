#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/do.sh staging build && $DIR/do.sh staging down && docker volume rm plebeian-market_buyer-app-static-content && $DIR/do.sh staging up -d
