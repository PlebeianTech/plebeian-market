#!/bin/sh

./do.sh prod build && ./do.sh prod down && ./do.sh prod up -d
