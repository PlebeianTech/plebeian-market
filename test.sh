#!/bin/sh

./do.sh test build && ./do.sh test up --abort-on-container-exit
