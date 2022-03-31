#!/bin/sh

USAGE="$0 (test|dev|prod) ..."

ENV=$1
shift

if [ "$ENV" = "test" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.test.yml $@
elif [ "$ENV" = "dev" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml $@
elif [ "$ENV" = "prod" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml $@
else
    echo $USAGE
    exit 1
fi
