#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/do.sh staging build && $DIR/do.sh staging down && $DIR/do.sh staging up -d
