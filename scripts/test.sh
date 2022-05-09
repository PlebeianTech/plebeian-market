#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/do.sh test build && $DIR/do.sh test up --abort-on-container-exit
