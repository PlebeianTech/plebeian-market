FROM python:3.10-bullseye

COPY ./api/requirements.txt /

RUN apt-get update \
 && apt-get install -y curl \
 && pip3 install -r /requirements.txt

COPY ./api /app

WORKDIR /app

ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1
