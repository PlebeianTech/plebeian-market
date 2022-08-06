#!/bin/sh

CONTAINER_NAME=$1
shift

docker exec -e FLASK_APP=main -it `docker ps -aqf "name=$CONTAINER_NAME"` $@
