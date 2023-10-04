FROM python:3.12-slim-bullseye

COPY ./ln_payments_processor/requirements.txt /

RUN apt-get update \
 && apt-get install -y curl git libpq-dev pkg-config cmake python3-magic \
 && pip3 install -r /requirements.txt

COPY ./ln_payments_processor /app

WORKDIR /app

ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1
