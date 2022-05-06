FROM nginx:1.19-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY ./services/nginx/nginx.conf /etc/nginx/conf.d/nginx.conf

EXPOSE 80
