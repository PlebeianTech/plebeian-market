## Advanced install options

### Install just the front office (from git master)

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
  "admin_pubkeys": [
      "123456789012345678901234567890",
      "another_admin_nostr_public_key"
  ]
  ```

* Copy the content of the `web/frontoffice/build` directory to your web server using your app of choice.

### Install the entire marketplace

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

## Development

### Front office (buyer part of the app)

#### Build the static files

```npm run build``` - Build static files

All the generated static files will be inside the `build` folder. You can copy them to your server to use the frontoffice on your website.

#### Run the app locally for development

```npm i``` - Install npm dependencies

```npm run dev``` - Run the app

### Back office (seller part of the app)

### Running the dev environment locally

```./scripts/test.sh``` to run the automated tests for the API

```./scripts/dev.sh``` to start the development environment: database, API and all background services

```cd web/backoffice && npm run dev``` to run the web app

### Background services

```finalize-auctions``` - monitors running auctions and picks a winner for auctions that ended

```settle-btc-payments``` - monitors on-chain payments that are "pending" in our database and looks up the corresponding transactions in the mempool or on-chain

```settle-lightning-payments``` - monitors incoming Lightning Network payments from buyers, and make outgoing payments to sellers

## Nostr

### Used event kinds

* 30017 - market stall
* 30018 - fixed price product listing
* 30020 - auction
* 1021 - bid
* 1022 - bid confirmation

### Stall chat

In order to have Stall chats, we fake a Nostr channel creation (kind = 40) but don't send the event to the network.
In this way, we're able to have chat rooms without polluting the chat room list in the clients. So if you want to
use this chat room in your client, you'll have to copy the channel id manually instead of searching for it.

Give a look to the `getChannelIdForStall` function to know how we're generating the Channel id.

## Keys used in the code

* `VITE_NOSTR_MARKET_SQUARE_CHANNEL_ID` - Nostr channel id of the Market Square for each community
* `VITE_NOSTR_PM_STALL_PUBLIC_KEY` - Nostr public key of Plebeian Market's market stall
