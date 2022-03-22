#!/bin/sh

docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.test.yml down --volumes
