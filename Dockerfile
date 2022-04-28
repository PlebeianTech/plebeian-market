FROM python:3.8-bullseye

COPY ./server/requirements.txt /
RUN apt-get update \
 && apt-get install -y curl \
 && pip3 install -r /requirements.txt

COPY ./server /app/server
COPY ./web /app/web

WORKDIR /app/server

ENV PYTHONPATH /app/server
ENV PYTHONUNBUFFERED 1
