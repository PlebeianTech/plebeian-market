#!/bin/sh

docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.test.yml up --abort-on-container-exit
