FROM python:3.11-bullseye

COPY ./birdwatcher/requirements.txt /

RUN apt-get update \
 && apt-get install -y curl \
 && pip3 install -r /requirements.txt

COPY ./birdwatcher /app

WORKDIR /app

ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1
