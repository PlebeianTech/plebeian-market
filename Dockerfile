FROM python:3.8-bullseye

COPY requirements.txt /
RUN apt-get update && apt-get install -y curl \
 && pip3 install -r /requirements.txt

COPY ./plebbid /app/plebbid
COPY ./start.sh /app/
WORKDIR /app

ENV PYTHONPATH=/app

EXPOSE 80

CMD ["./start.sh"]
