#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/do.sh staging down --volumes && $DIR/do.sh staging build && $DIR/do.sh staging up -d
