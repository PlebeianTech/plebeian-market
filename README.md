# Plebeian Market

<p align="center">
  <img src="https://plebeian.market/images/logo.png" width="256" title="Plebeian Market">
</p>

## About

**Plebeian Market** is the self-sovereign marketplace of the Internet, powered by Bitcoin and the Lightning Network for payments and by Nostr for resilience.

What you see here is the initial implementation of a larger vision of fully decentralized e-commerce.

While we are also running *[plebeian.market](https://plebeian.market/)* - a Plebeian Market instance - others can, and are encouraged to, run their own instances. Whether on your own hardware using Umbrel or Start9 or on a VPS, running a Plebeian Market instance is what makes your community self-sovereign and in control of its data.

Our vision of the future involves small communities around the world running their own market places, which is why we like to call Plebeian Market *the mycelium of free commerce*.

## Architecture

To achieve resilience, the marketplace has two independent components: the **back office** and the **front office**.

Merchants use the **back office** to create listings, which are forwarded to known Nostr relays. The **back office** does therefore not need to be accessible from the Internet - it can be hosted on an Umbrel or Start9 running in one's closet. This ensures that the merchants are always in control of their data!

Buyers use the **front office** to make purchases. This is a *client-side* web app, that doesn't talk to the **back office** (remember, the back office might not be accessible on the Internet!), and only talks to Nostr relays. This app can therefore be hosted on something as simple as GitHub pages - or it can even be sent around using email! A merchant could indeed, in theory, email a `.html` page to its customers, which, when opened, connects to Nostr relays, displays the merchant's stall, takes orders from the buyers, and forwards the orders back to the Nostr relays.

The **back office** then connects to the known Nostr relays, fetches the orders that the buyers have placed and replies back with invoices that the buyers need to pay.

## Install

### Linode (or any other VPS provider)

1. Create a new Linode, in the region you want. The cheapest one (Nanode, 5$, shared CPU) should be enough. Select Debian 12 as an OS. **Set a strong root password and write it down!**
1. Once the machine is created, copy the IP address, go to your DNS settings, and create an `A` record, pointing from your desired host name to the IP of the machine.
1. Open a terminal.
1. Wait a couple of minutes for the DNS to propagate. It shouldn't take long. You can run `ping <domain name>` in the terminal you opened and see that the results include the correct IP address.
1. Log in to your machine using `ssh root@<domain name>`. Respond with `yes` to any questions about trusting the host and use the root password from step 1!
1. Run `sh -c "$(curl -sSL https://raw.githubusercontent.com/PlebeianTech/plebeian-market/master/install.sh)"`
