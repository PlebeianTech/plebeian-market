FROM node:16-alpine AS builder

ARG BUILD_MODE

COPY ./web /web

RUN cd /web/backoffice \
 && npm install \
 && npm run build$BUILD_MODE

FROM node:16-alpine

WORKDIR /app
COPY --from=builder /web/backoffice/build .
COPY --from=builder /web/backoffice/package.json .
COPY --from=builder /web/backoffice/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "index.js"]
