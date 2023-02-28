# Plebeian Market

## About

**Plebeian Market** is the self-sovereign marketplace of the internet, powered by Bitcoin and the Lightning Network for payments and by Nostr for communications.

What you see here is the initial implementation of a larger vision of fully decentralized e-commerce.

While we are also running *plebeian.market* - a Plebeian Market instance - others can, and are encouraged to, run their own instances. Whether on your own hardware using Umbrel or Start9 or on a VPS, running a Plebeian Market instance is what makes your community self-sovereign and in control of its data.

Our vision of the future involves small communities around the world running their own market places. At the same time, these market places will communicate with each other, which is why we like to call Plebeian Market *the mycelium of free commerce*.

## Developement

### Running the dev environment locally

```./scripts/test.sh``` to run the automated tests for the API

```./scripts/dev.sh``` to start the development environment: database, API and all background services

```cd web && npm run dev``` to run the web app

### Background services

```finalize-auctions``` - monitors running auctions and picks a winner for auctions that ended

```settle-lnd-payments``` - subscribes to LND for settled invoices and marks pending payments in our database as "settled"

```settle-btc-payments``` - monitors on-chain payments that are "pending" in our database and looks up the corresponding transactions in the mempool or on-chain

```process-notifications``` - sends notifications
