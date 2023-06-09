FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./services/nginx/nginx.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 80
