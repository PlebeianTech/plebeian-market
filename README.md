# Plebeian Market

<p align="center">
  <img src="https://plebeian.market/images/logo.png" width="256" title="Plebeian Market">
</p>

## About

**Plebeian Market** is the self-sovereign marketplace of the internet, powered by Bitcoin and the Lightning Network for payments and by Nostr for communications.

What you see here is the initial implementation of a larger vision of fully decentralized e-commerce.

While we are also running *plebeian.market* - a Plebeian Market instance - others can, and are encouraged to, run their own instances. Whether on your own hardware using Umbrel or Start9 or on a VPS, running a Plebeian Market instance is what makes your community self-sovereign and in control of its data.

Our vision of the future involves small communities around the world running their own market places. At the same time, these market places will communicate with each other, which is why we like to call Plebeian Market *the mycelium of free commerce*.

## Skills Market

The *Skills Market* is a place where you can publish your professional CV/résumé or browse CVs other bitcoiners have published. This section of the market place is **entirely powered by the Nostr protocol**, using the event of `kind=66`. This event uses a `content` in JSON format with the following structure:

```
{
  job_title: string,
  bio: string,
  desired_yearly_salary_usd: number | null,
  hourly_rate_usd: number | null,
  bitcoiner_question: string,
  skills: [{skill: string}, {skill: string}, ...],
  portfolio: [{url: string}, {url: string}, ...],
  education: [{education: string, year: number | null}, {education: string, year: number | null}, ...],
  experience: [{job_title: string, organization: string, description: string, from_year: number | null, from_month: number | null, to_year: number | null, to_month: number | null}, {job_title: string, organization: string, description: string, from_year: number | null, from_month: number | null, to_year: number | null, to_month: number | null}, ...],
  achievements: [{achievement: string, year: number | null}, {achievement: string, year: number | null}, ...],
 }
}
```



## Development

### Frontstore (buyer part of the app)

#### Build the static files

```npm run build``` - Build static files

All the generated static files will be inside the `build` folder. You can copy them to your server to use the frontstore on your website.

#### Run the app locally for development

```npm i``` - Install npm dependencies

```npm run dev``` - Run the app


### Backstore (seller part of the app)



### Running the dev environment locally

```./scripts/test.sh``` to run the automated tests for the API

```./scripts/dev.sh``` to start the development environment: database, API and all background services

```cd web && npm run dev``` to run the web app

### Background services

```finalize-auctions``` - monitors running auctions and picks a winner for auctions that ended

```settle-lnd-payments``` - subscribes to LND for settled invoices and marks pending payments in our database as "settled"

```settle-btc-payments``` - monitors on-chain payments that are "pending" in our database and looks up the corresponding transactions in the mempool or on-chain

```process-notifications``` - sends notifications


## Non-standard nip-15 extension

### Stall chat

In order to have Stall chats, we fake a Nostr channel creation (kind = 40) but don't send the event to the network.
In this way, we're able to have chat rooms without polluting the chat room list in the clients. So if you want to
use this chat room in your client, you'll have to copy the channel id manually instead of searching for it.

Give a look to the `getChannelIdForStall` function to know how we're generating the Channel id.
