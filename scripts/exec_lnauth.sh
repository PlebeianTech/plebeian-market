#!/bin/sh

DIR="$(cd "$(dirname "$0")" && pwd)"

KEY=$1

$DIR/exec.sh api flask lnauth $1
