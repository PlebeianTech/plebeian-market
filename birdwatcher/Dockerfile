FROM python:3.11-slim-bookworm

COPY ./birdwatcher/requirements.txt /

RUN apt-get update \
 && apt-get install -y wget gcc \
 && pip3 install -r /requirements.txt \
 && echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends firefox

COPY ./birdwatcher /app

WORKDIR /app

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux32.tar.gz \
 && tar xzfv geckodriver-v0.33.0-linux32.tar.gz && rm geckodriver-v0.33.0-linux32.tar.gz \
 && chmod +x geckodriver && chown root:root geckodriver

ENV PYTHONPATH /app
ENV PYTHONUNBUFFERED 1
