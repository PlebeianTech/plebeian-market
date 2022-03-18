#!/bin/sh

gunicorn --chdir /app plebbid.main:app -w 2 --threads 2 -b 0.0.0.0:80 --log-level=debug
