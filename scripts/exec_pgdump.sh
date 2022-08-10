#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

$DIR/exec.sh plebeian-market-db-1 pg_dump -Upleb market
