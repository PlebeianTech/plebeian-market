#!/bin/sh

do_job_web () {
    gunicorn --chdir /app plebbid.main:app -w 2 --threads 2 -b 0.0.0.0:80 --log-level=debug
}

do_job_settle_bids () {
    flask settle-bids
}

case "$JOB" in
  "SETTLE_BIDS") do_job_settle_bids ;;
  *) do_job_web ;;
esac
