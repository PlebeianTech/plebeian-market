FROM node:16-alpine AS builder

COPY ./web /web

RUN cd /web && npm install && npm run build && npm run buildcss

FROM nginx:1.19-alpine

ARG BUILD_ID
ENV BUILD_ID=$BUILD_ID

RUN rm /etc/nginx/conf.d/default.conf
COPY ./services/nginx/nginx.conf.template /nginx.conf.template
RUN envsubst '$BUILD_ID' < /nginx.conf.template > /etc/nginx/conf.d/nginx.conf

COPY --from=builder /web/app /usr/share/nginx/html/app/
COPY --from=builder /web/static /usr/share/nginx/html/static/

EXPOSE 80
