# Development

This documentation will guide you through setting up a local development environment to contribute to the Plebeian Market. If you have not read the repository README, please take a look, as it will help you understand the project's architecture.

It is important to note that the Plebeian stack consists of the front office, back office, and background services. If your intention is to do front-end development, the background services are not strictly necessary, but you will need to run them if you want to have the full functionality of the application and populate the front-end (front or back office) with some data.

## Running the Dev Environment Locally

### Prerequisites

- You need to have the Docker Engine installed on your system. You can follow the official instructions: [Install Docker engine](https://docs.docker.com/engine/install/)
  - If you are on Linux, you'll want to install Docker in a different user using `useradd -m -G docker YOUR_USER`, and also follow the post-installation steps: [Docker post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/)
- You need to have Node.js >= 16 and npm installed on your machine.
- Git clone this repository in the directory of the user you will use, using `git clone git@github.com:PlebeianTech/plebeian-market.git`

### Running Dev Environment

#### Background Services

- Once you have cloned the repository, open a terminal in the `plebeian-market` project directory and run `./scripts/dev.sh` to start the development environment: database, API, and all background services
  - There will be some background services that will exit with errors like smtp and birdwatcher, don't worry, they are not necessary for development. If you now run `docker ps` in your terminal, you will see the different containers running.

#### Back Office (Seller Part of the App)

- First, go to `web/shared` with `cd web/shared` and run `npm i`
- Then go to the `backoffice` directory with `cd web/backoffice` and run `npm i`, and then `npm run dev` to run the web app
- This will start the development server of the `backoffice`, and you will be able to access it from `localhost:5173` in your browser
- **Tip**: To complete the process of creating a stall, you will need the email verification code, as smtp does not work in the development environment. You will need to get it from the logs of the `api` container. To do this, you can do `docker logs -f plebeian-market-api-1` and this will show you the logs of the api. If you are going through the create stall process, the email verification code will appear in these logs.

#### Front Office (Buyer Part of the App)

- If you have not previously installed `shared` node dependencies: go to `web/shared` with `cd web/shared` and run `npm i`
- Then go to the `frontoffice` directory with `cd web/frontoffice` and run `npm i`, and then `npm run dev` to run the web app
- This will start the development server of the `frontoffice` successfully, and you will be able to access it from `localhost:5173` or `localhost:5174` (if you are running backoffice at the same time) in your browser

#### Build/Preview the Static Files

- If you want to build or preview, you can do so using these commands in the front or back office directories
- `npm run preview` - Build static files and serve them using a http server
- `npm run build` - Build static files

All the generated static files will be inside the `build` folder. You can copy them to your server to use the `frontoffice` on your website.

### Background Services

```finalize-auctions``` - monitors running auctions and picks a winner for auctions that ended

```settle-btc-payments``` - monitors on-chain payments that are "pending" in our database and looks up the corresponding transactions in the mempool or on-chain

```settle-lightning-payments``` - monitors incoming Lightning Network payments from buyers, and makes outgoing payments to sellers

## Nostr

### Used Event Kinds

* 30017 - market stall
* 30018 - fixed price product listing
* 30020 - auction
* 1021 - bid
* 1022 - bid confirmation

### Stall Chat

In order to have Stall chats, we fake a Nostr channel creation (kind = 40) but don't send the event to the network. In this way, we're able to have chat rooms without polluting the chat room list in the clients. So if you want to use this chat room in your client, you'll have to copy the channel id manually instead of searching for it.

Give a look to the `getChannelIdForStall` function to know how we're generating the Channel id.

## Keys Used in the Code

* `VITE_NOSTR_MARKET_SQUARE_CHANNEL_ID` - Nostr channel id of the Market Square for each community
* `VITE_NOSTR_PM_STALL_PUBLIC_KEY` - Nostr public key of Plebeian Market's market stall

## Advanced Install Options

### Install Just the Front Office (from Git Master)

* Clone the repository
`git clone git@github.com:PlebeianTech/plebeian-market.git`

* Change to the front office directory
`cd plebeianmarket/web/frontoffice`

* Build the site
`npm i ; npm run build`

* (optional) Copy the file config-example.json to config.json:
  `cd web/frontoffice/build ; cp config-example.json config.json`

* (optional) Edit the `config.json` file and add your Nostr public key to the `admin_pubkeys` array:
  ```
  "admin\_pubkeys": [
      "123456789012345678901234567890",
      "another\_admin\_nostr\_public\_key"
  ]
  ```

* Copy the content of the `web/frontoffice/build` directory to your web server using your app of choice.

### Install the Entire Marketplace

* install [`nginx-proxy-automation`](https://github.com/evertramos/nginx-proxy-automation)
* clone repo
* add `plebeian-market-secrets/secret_key` (random string)
* add `plebeian-market-secrets/db.json` (default username: *pleb* / default password: *plebpass*)
* add `plebeian-market-secrets/lndhub.json`
* add `plebeian-market-secrets/mail.json`
* add `plebeian-market-secrets/site-admin.json`
* edit `.env.prod`
  * `API_BASE_URL`, `WWW_BASE_URL`, `DOMAIN_NAME`
* edit `docker-compose.prod.yml`
  * `VIRTUAL_HOST`, `LETSENCRYPT_HOST`
* `flask db upgrade`
* `./scripts/prod.sh`