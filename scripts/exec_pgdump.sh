#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/exec.sh db pg_dump -Upleb market
