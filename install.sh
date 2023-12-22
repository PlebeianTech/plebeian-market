#!/bin/sh

# on a fresh machine:
# adduser www
# usermod -aG sudo www
# sudo su - www
# then, run this script!

docker -v
if [ $? -ne 0 ]; then
    echo "Docker not installed. Installing..."

    sudo apt-get update
    sudo apt-get -y install ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker $USER
    newgrp docker
fi

sudo apt-get -y install git

echo -n "Enter your domain name: "
read DOMAIN_NAME

echo -n "Enter your email: "
read EMAIL

cd
echo "Installing Nginx proxy automation..."
git clone --recurse-submodules https://github.com/evertramos/nginx-proxy-automation.git proxy
cd proxy/bin && ./fresh-start.sh --yes --skip-docker-image-check -e $EMAIL
./test.sh $DOMAIN_NAME

CONTINUE=n
while [ $CONTINUE != y ]
do
    echo "Continue? [y/n]"
    read CONTINUE
done

cd
mkdir plebeian-market-secrets
tr -dc A-Za-z0-9 </dev/urandom | head -c 64 > plebeian-market-secrets/secret_key
echo "{\"USERNAME\": \"pleb\", \"PASSWORD\": \"plebpass\"}" > plebeian-market-secrets/db.json
echo "{\"LNDHUB_URL\": \"https://ln.getalby.com\", \"LNDHUB_USER\": \"TODO\", \"LNDHUB_PASSWORD\": \"TODO\"}" > plebeian-market-secrets/lndhub.json
echo "{\"server\": \"\", \"username\": \"\", \"password\": \"\", \"default_sender\": \"hello@plebeian.market\"}" > plebeian-market-secrets/mail.json
echo "{\"NSEC\": \"\"}" > plebeian-market-secrets/nostr.json
echo "{\"NSEC\": \"\", \"XPUB\": \"\", \"LIGHTNING_ADDRESS\": \"\"}" > plebeian-market-secrets/site-admin.json

cat << EOF > .env.api
ENV=prod
FLASK_APP=main
LOG_LEVEL=INFO
BIRDWATCHER_BASE_URL=http://birdwatcher:6000
LNDHUB_URL=https://ln.getalby.com
LOG_FILENAME=/state/pm.log
PROCESSED_EVENT_IDS_FILENAME=/state/processed_event_ids.txt
VERIFIED_EXTERNAL_IDENTITIES_FILENAME=/state/verified_external_identities.txt
GECKODRIVER_BINARY=/app/geckodriver
EOF
echo "DOMAIN_NAME=$DOMAIN_NAME" >> .env.api
echo "WWW_BASE_URL=https://$DOMAIN_NAME" >> .env.api
echo "API_BASE_URL=https://$DOMAIN_NAME" >> .env.api

cat << EOF > .env.nginx
VIRTUAL_HOST=$DOMAIN_NAME
LETSENCRYPT_HOST=$DOMAIN_NAME
EOF

cat << EOF > .env.web
VITE_NOSTR_MARKET_SQUARE_CHANNEL_ID="TODO"
VITE_NOSTR_PM_STALL_ID="TODO"
VITE_NOSTR_PM_STALL_PUBLIC_KEY="TODO"
EOF
echo "VITE_BASE_URL=https://$DOMAIN_NAME/" >> .env.web
echo "VITE_API_BASE_URL=https://$DOMAIN_NAME/" >> .env.web

cat << EOF > docker-compose.yml
version: '3.6'

services:
  db:
    image: ghcr.io/plebeiantech/plebeian-market-db
    networks:
      - db_network
    volumes:
      - "/home/www/plebeian-market-dbdata:/var/lib/postgresql/data"
  relay:
    image: ghcr.io/plebeiantech/plebeian-market-relay
    networks:
      - proxy
    ports:
      - "7777:7777"
    volumes:
      - "/home/www/plebeian-market-relaydata:/app/strfry-db"
  api:
    image: ghcr.io/plebeiantech/plebeian-market-api
    depends_on: [db]
    restart: on-failure
    stop_grace_period: 1m
    networks:
      - db_network
      - proxy
    volumes:
      - "/home/www/plebeian-market-secrets:/secrets"
      - "/home/www/plebeian-market-state:/state"
    env_file: .env.api
    command: gunicorn --preload --chdir /app main:app -w 2 --threads 2 -b 0.0.0.0:8080
  birdwatcher:
    image: ghcr.io/plebeiantech/plebeian-market-birdwatcher
    restart: on-failure
    stop_grace_period: 15s
    networks:
      - db_network
    volumes:
      - "/home/www/plebeian-market-secrets:/secrets"
      - "/home/www/plebeian-market-state:/state"
    command: python main.py
  web:
    image: ghcr.io/plebeiantech/plebeian-market-web
    depends_on:
      - api
    networks:
      - proxy
    env_file: .env.web
    volumes:
      - "buyer-app-static-content:/buyer-app"
  nginx:
    image: ghcr.io/plebeiantech/plebeian-market-nginx
    env_file: .env.nginx
    depends_on:
      - api
      - web
    networks:
      - proxy
    volumes:
      - "buyer-app-static-content:/buyer-app"

networks:
  db_network:
    driver: bridge
  relay_network:
    driver: bridge
  proxy:
    driver: bridge

volumes:
  buyer-app-static-content:
EOF

