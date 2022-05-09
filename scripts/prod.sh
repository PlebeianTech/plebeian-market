#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/do.sh prod build && $DIR/do.sh prod down && $DIR/do.sh prod up -d
