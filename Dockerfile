FROM python:3.8-bullseye

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./plebbid /app/plebbid
COPY ./gunicorn.sh /app/
WORKDIR /app

ENV PYTHONPATH=/app

CMD ["./gunicorn.sh"]
