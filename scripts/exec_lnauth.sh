#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

KEY=$1

$DIR/exec.sh plebeian-market-api-1 flask lnauth $1
