FROM node:18-alpine AS builder

ARG BUILD_MODE

COPY ./web /web

COPY ./install.sh /web/frontoffice/static/

RUN cd /web/shared \
 && npm install

RUN cd /web/frontoffice \
 && npm install \
 && npm run build$BUILD_MODE

RUN cd /web/backoffice \
 && npm install \
 && npm run build$BUILD_MODE

FROM node:18-alpine

WORKDIR /front-office-app
COPY --from=builder /web/frontoffice/build .

WORKDIR /app
COPY --from=builder /web/backoffice/build .
COPY --from=builder /web/backoffice/package.json .
COPY --from=builder /web/backoffice/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "index.js"]
