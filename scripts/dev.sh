#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/do.sh dev up --build
