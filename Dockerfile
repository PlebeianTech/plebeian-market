FROM python:3.8-bullseye

COPY requirements.txt /
RUN apt-get update && apt-get install -y curl \
 && pip3 install -r /requirements.txt

COPY ./plebeianmarket /app/plebeianmarket
COPY ./client /app/client
WORKDIR /app

ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1
