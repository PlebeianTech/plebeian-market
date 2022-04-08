FROM node:16-alpine AS builder

COPY ./client /client

RUN cd /client && npm install && npm run build

FROM nginx:1.19-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./services/nginx/nginx.conf /etc/nginx/conf.d

COPY --from=builder /client/app /usr/share/nginx/html/app/
COPY ./client/static /usr/share/nginx/html/static/

EXPOSE 80
