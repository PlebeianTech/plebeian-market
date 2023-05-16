FROM node:16-alpine AS builder

ARG BUILD_MODE

COPY ./web /web

RUN cd /web/frontoffice \
 && npm install \
 && npm run build \

WORKDIR /buyer-app
COPY --from=builder /web/frontoffice/build .

RUN cd /web/backoffice \
 && npm install \
 && npm run build$BUILD_MODE

WORKDIR /app
COPY --from=builder /web/backoffice/build .
COPY --from=builder /web/backoffice/package.json .
COPY --from=builder /web/backoffice/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "index.js"]
