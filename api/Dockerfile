FROM python:3.12-slim-bullseye

COPY ./api/requirements.txt /

RUN apt-get update \
 && apt-get install -y curl git libpq-dev pkg-config gcc cmake python3-magic \
 && pip3 install -r /requirements.txt

COPY ./api /app

WORKDIR /app

ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1
