FROM node:16-alpine AS builder

COPY ./web /web

RUN cd /web \
 && npm install \
 && npm run build

FROM node:16-alpine

WORKDIR /app
COPY --from=builder /web/build .
COPY --from=builder /web/package.json .
COPY --from=builder /web/node_modules ./node_modules

EXPOSE 3000
CMD ["node", "index.js"]
