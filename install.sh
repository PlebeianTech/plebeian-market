#!/bin/sh

docker -v
if [ $? -ne 0 ]; then
    echo "Docker not installed. Installing..."

    apt-get update
    apt-get -y install ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

apt-get -y install git

if [ ! -f plebeian-market-certificates/cert.pem -o ! -f plebeian-market-secrets/mail.json -o ! -f .env -o ! -f plebeian-market-nginx/app.conf ]; then
  echo "------------------------"
  echo -n "Enter your domain name (the DNS must be already configured at this point!): "
  read DOMAIN_NAME
  echo -n "Enter an email address (this will be used to obtain SSL certificates on your behalf): "
  read EMAIL
fi

cd && mkdir -p plebeian-market-certificates
if [ ! -f plebeian-market-certificates/cert.pem ]; then # TODO: probably better to name the certificate after the domain
  echo "------------------------"
  echo "Obtaining SSL certificates. This may take a while..."
  echo "------------------------"
  docker run --rm -it -v "$(pwd)/out":/acme.sh --net=host neilpang/acme.sh --register-account --server letsencrypt -m $EMAIL
  docker run --rm -it -v "$(pwd)/out":/acme.sh --net=host neilpang/acme.sh --issue --server letsencrypt -d $DOMAIN_NAME --standalone
  docker run --rm -it -v "$(pwd)/out":/acme.sh -v "$(pwd)/plebeian-market-certificates":/cert --net=host neilpang/acme.sh --install-cert -d $DOMAIN_NAME --key-file /cert/key.pem --fullchain-file /cert/cert.pem
fi

# TODO: configure SITE_NAME

cd && mkdir -p plebeian-market-secrets
if [ ! -f plebeian-market-secrets/secret_key ]; then
  tr -dc A-Za-z0-9 </dev/urandom | head -c 64 > plebeian-market-secrets/secret_key
fi
if [ ! -f plebeian-market-secrets/nostr.json ]; then
  NOSTR_PRIVATE_KEY=`openssl rand -hex 32`
  NSEC=`docker run --rm ghcr.io/rot13maxi/key-convertr:main --kind nsec $NOSTR_PRIVATE_KEY`
  echo "{\"NSEC\": \"$NSEC\"}" > plebeian-market-secrets/nostr.json
fi
if [ ! -f plebeian-market-secrets/db.json ]; then
  echo "{\"USERNAME\": \"pleb\", \"PASSWORD\": \"plebpass\"}" > plebeian-market-secrets/db.json
fi
if [ ! -f plebeian-market-secrets/lndhub.json ]; then
  echo "{\"LNDHUB_URL\": \"https://ln.getalby.com\", \"LNDHUB_USER\": \"TODO\", \"LNDHUB_PASSWORD\": \"TODO\"}" > plebeian-market-secrets/lndhub.json
fi
if [ ! -f plebeian-market-secrets/mail.json ]; then
  echo "{\"server\": \"smtp\", \"username\": \"\", \"password\": \"\", \"default_sender\": \"hello@$DOMAIN_NAME\"}" > plebeian-market-secrets/mail.json
fi

cd && mkdir -p plebeian-market-state/media && mkdir -p plebeian-market-state/front-office-config

if [ ! -f plebeian-market-state/front-office-config/config.json ]; then
  MARKET_SQUARE_CHANNEL_ID=`openssl rand -hex 32`
  echo "{\"admin_pubkeys\": [\"TODO\"], \"homepage_banner_image\": \"\", \"backend_present\": true, \"market_square_channel_id\": \"$MARKET_SQUARE_CHANNEL_ID\" }" > plebeian-market-state/front-office-config/config.json
fi

if [ ! -f .env ]; then
  cat << EOF > .env
ENV=prod
FLASK_APP=main
LOG_LEVEL=INFO
BIRDWATCHER_BASE_URL=http://birdwatcher:6000
LNDHUB_URL=https://ln.getalby.com
LOG_FILENAME=/state/pm.log
PROCESSED_EVENT_IDS_FILENAME=/state/processed_event_ids.txt
VERIFIED_EXTERNAL_IDENTITIES_FILENAME=/state/verified_external_identities.txt
GECKODRIVER_BINARY=/app/geckodriver
USER_EMAIL_VERIFICATION=0
EOF
  echo "DOMAIN_NAME=$DOMAIN_NAME" >> .env
  echo "WWW_BASE_URL=https://$DOMAIN_NAME" >> .env
  echo "API_BASE_URL=https://$DOMAIN_NAME" >> .env
  echo "ALLOWED_SENDER_DOMAINS=$DOMAIN_NAME" >> .env
fi

cd && mkdir -p plebeian-market-nginx
if [ ! -f plebeian-market-nginx/app.conf ]; then
  cat << EOF > plebeian-market-nginx/app.conf
upstream plebeianmarketapi {
    server api:8080;
}

upstream plebeianmarketweb {
    server web:3000;
}

upstream plebeianmarketrelay {
    server relay:7777;
}
server {
    listen 80;
    server_name $DOMAIN_NAME;
    location / {
        return 301 https://\$host\$request_uri;
    }
}
server {
    listen 443 ssl;
    client_max_body_size 10M;
    server_name $DOMAIN_NAME;
    ssl_certificate /cert/cert.pem;
    ssl_certificate_key /cert/key.pem;
    location /admin {
        proxy_pass http://plebeianmarketweb;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_redirect off;
    }
    location /api {
        add_header Access-Control-Allow-Origin *;
        proxy_pass http://plebeianmarketapi;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_redirect off;
    }
    location /relay {
        add_header Access-Control-Allow-Origin *;
        proxy_pass http://plebeianmarketrelay;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
        proxy_redirect off;
    }
    location /media {
        alias /media/;
    }
    location /front-office-config {
        alias /front-office-config/;
    }
    location / {
        add_header Access-Control-Allow-Origin *;
        root /front-office-app;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
}
EOF
fi # plebeian-market-nginx/app.conf

if [ ! -f update.sh ]; then
  cat << EOF > update.sh
#!/bin/sh

cd

if [ ! -f plebeian-market-state/UPDATE_REQUESTED ]; then
    exit 0
fi

touch plebeian-market-state/UPDATE_RUNNING && rm plebeian-market-state/UPDATE_REQUESTED

docker compose pull >> plebeian-market-state/UPDATE_RUNNING 2>&1
if [ $? -ne 0 ]; then
    mv plebeian-market-state/UPDATE_RUNNING plebeian-market-state/UPDATE_FAILED
    exit 1
fi

docker compose down --volumes >> plebeian-market-state/UPDATE_RUNNING 2>&1
if [ $? -ne 0 ]; then
    mv plebeian-market-state/UPDATE_RUNNING plebeian-market-state/UPDATE_FAILED
    exit 1
fi

docker compose up -d >> plebeian-market-state/UPDATE_RUNNING 2>&1
if [ $? -ne 0 ]; then
    mv plebeian-market-state/UPDATE_RUNNING plebeian-market-state/UPDATE_FAILED
    exit 1
fi

mv plebeian-market-state/UPDATE_RUNNING plebeian-market-state/UPDATE_SUCCESS
EOF
  crontab -l | { cat; echo "* * * * * /bin/sh /root/update.sh"; } | crontab -
fi # update.sh

if [ ! -f docker-compose.yml ]; then
  cat << EOF > docker-compose.yml
version: '3.6'

services:
  db:
    image: ghcr.io/plebeiantech/plebeian-market-db
    restart: always
    networks:
      - db_network
    volumes:
      - "./plebeian-market-dbdata:/var/lib/postgresql/data"
  relay:
    image: ghcr.io/plebeiantech/plebeian-market-relay
    restart: always
    networks:
      - web_network
    ports:
      - "7777:7777"
    volumes:
      - "./plebeian-market-relaydata:/app/strfry-db"
  smtp:
    image: ghcr.io/plebeiantech/plebeian-market-smtp
    restart: always
    networks:
      - smtp_network
    ports:
      - "1587:587"
    env_file: .env
  api:
    image: ghcr.io/plebeiantech/plebeian-market-api
    depends_on: [db]
    restart: always
    stop_grace_period: 1m
    networks:
      - db_network
      - smtp_network
      - web_network
    volumes:
      - "./plebeian-market-secrets:/secrets"
      - "./plebeian-market-state:/state"
    env_file: .env
    command: bash -c "flask db upgrade && flask configure-default-relays && gunicorn --preload --chdir /app main:app -w 2 --threads 2 -b 0.0.0.0:8080"
  finalize-auctions:
    image: ghcr.io/plebeiantech/plebeian-market-api
    depends_on: [db]
    restart: always
    stop_grace_period: 1m
    networks:
      - db_network
    volumes:
      - "./plebeian-market-secrets:/secrets"
      - "./plebeian-market-state:/state"
    env_file: .env
    command: flask finalize-auctions
  settle-btc-payments:
    image: ghcr.io/plebeiantech/plebeian-market-api
    depends_on: [db]
    restart: always
    stop_grace_period: 1m
    networks:
      - db_network
      - smtp_network
    volumes:
      - "./plebeian-market-secrets:/secrets"
      - "./plebeian-market-state:/state"
    env_file: .env
    command: flask settle-btc-payments
  birdwatcher:
    image: ghcr.io/plebeiantech/plebeian-market-birdwatcher
    restart: always
    stop_grace_period: 15s
    networks:
      - db_network
    volumes:
      - "./plebeian-market-secrets:/secrets"
      - "./plebeian-market-state:/state"
    env_file: .env
    command: python main.py
  web:
    image: ghcr.io/plebeiantech/plebeian-market-web
    restart: always
    networks:
      - web_network
    depends_on:
      - api
    env_file: .env
    volumes:
      - "front-office-app:/front-office-app"
  nginx:
    image: nginx:1.25-alpine-slim
    restart: always
    networks:
      - web_network
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api
      - web
    volumes:
      - "./plebeian-market-nginx:/etc/nginx/conf.d"
      - "./plebeian-market-certificates:/cert"
      - "./plebeian-market-state/media:/media"
      - "./plebeian-market-state/front-office-config:/front-office-config"
      - "front-office-app:/front-office-app"

networks:
  db_network:
    driver: bridge
  smtp_network:
    driver: bridge
  web_network:
    driver: bridge

volumes:
  front-office-app:
EOF
fi # docker-compose.yml

echo "------------------------"
echo "(RE)Starting the app!"
echo "------------------------"

docker compose down --volumes && docker compose pull && docker compose up -d

echo "------------------------"
echo "All is well! Try navigating to https://$DOMAIN_NAME using your browser!"
echo "------------------------"
