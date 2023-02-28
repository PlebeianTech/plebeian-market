# Plebeian Market

## Running the dev environment locally

```./scripts/test.sh``` to run the automated tests for the API

```./scripts/dev.sh``` to start the development environment: database, API and all background services

```cd web && npm run dev``` to run the web app

## Background services

```finalize-auctions``` - monitors running auctions and picks a winner for auctions that ended

```settle-lnd-payments``` - subscribes to LND for settled invoices and marks pending payments in our database as "settled"

```settle-btc-payments``` - monitors on-chain payments that are "pending" in our database and looks up the corresponding transactions in the mempool or on-chain

```process-notifications``` - sends notifications
