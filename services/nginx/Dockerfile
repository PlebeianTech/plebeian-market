FROM nginx:1.25-alpine-slim

RUN mkdir /front-office-config && rm /etc/nginx/conf.d/default.conf
COPY ./web/frontoffice/static/config-pm.json /front-office-config/config.json
COPY ./services/nginx/nginx.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 80
