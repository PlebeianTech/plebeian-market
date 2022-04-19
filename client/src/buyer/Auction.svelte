<script>
    import { onMount } from 'svelte';
    import Time from 'svelte-time';
    import { token, fromJson, fetchAPI } from "../common.js";
    import Login from '../Login.svelte';

    $token = sessionStorage.getItem('token');

    export let key;
    if (window.location.hash.substring(1).startsWith('plebeian-auction-')) {
        key = window.location.hash.substring(1 + 'plebeian-auction-'.length);
    }

    let auction = null;
    let amount = null;
    let paymentRequest = null;
    let paymentQr = null;

    function nextBid(lastBid) {
        var head = String(lastBid).slice(0, 2);
        var rest = String(lastBid).slice(2);

        if (head[0] === "1") {
            head = String(Number(head) + 1);
        } else if (head[0] === "2") {
            head = String(Number(head) + 2);
        } else if (head[0] === "3" || head[0] === "4") {
            if (head[1] === "0") {
                head = head[0] + "2";
            } else if (head[1] === "1" || head[1] === "2" || head[1] === "3") {
                head = head[0] + "5";
            } else if (head[1] === "4" || head[1] === "5" || head[1] === "6" ||  head[1] === "7") {
                head = head[0] + "8";
            } else {
                head = String(Number(head[0]) + 1) + "0";
            }
        } else {
            if (head[1] === "0" || head[1] === "1" || head[1] === "2" || head[1] === "3") {
                head = head[0] + "5";
            } else {
                head = String(Number(head[0]) + 1) + "0";
            }
        }

        return Number(head + rest);
    }

    function placeBid() {
        fetchAPI(`/auctions/${key}/bids`, 'POST', $token,
            JSON.stringify({amount: amount}),
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        paymentRequest = data.payment_request;
                        paymentQr = data.qr;
                    });
                } else {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.indexOf('application/json') !== -1) {
                        response.json().then(data => { alert(`Error: ${data.message}`); })
                    } else {
                        return response.text().then(text => { console.log(`Error ${response.status}: ${text}`); });
                    }
                }
            });
    }

    function refreshAuction() {
        fetchAPI(`/auctions/${key}`, 'GET', $token,
            null,
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        auction = fromJson(data.auction);
                        var lastBid = auction.starting_bid;
                        for (const bid of auction.bids) {
                            if (bid.payment_request === paymentRequest) {
                                paymentQr = paymentRequest = amount = null;
                            }
                            lastBid = bid.amount;
                        }
                        if (!amount) {
                            amount = nextBid(lastBid);
                        }
                        setTimeout(refreshAuction, 1000);
                    });
                }
            }
        );
    }

    onMount(async () => { refreshAuction() });
</script>

{#if auction}
<div class="flex justify-center items-center">
    <div class="w-3/5 bg-gray-900 rounded p-4">
        <p class="text-zinc-300"><Time timestamp={auction.start_date} format="dddd MMMM D, H:mm" /> - <Time timestamp={auction.end_date} format="dddd MMMM D, H:mm - YYYY" /></p>
        <p class="text-zinc-300"><span>Starting bid: {auction.starting_bid}</span></p>
        <ul id="bids" class="text-zinc-300">
            {#each auction.bids as bid}
                <li>{bid.amount} (by {bid.bidder})</li>
            {/each}
        </ul>
        {#if $token}
            {#if auction.canceled}
                <div>Auction was canceled.</div>
            {:else if !auction.started}
                <div>Auction starts <Time live relative timestamp={auction.start_date} />.</div>
            {:else if auction.ended}
                <div>Auction ended <Time live relative timestamp={auction.end_date} />.</div>
            {:else}
                {#if paymentQr}
                    <div class="qr glowbox">
                        {@html paymentQr}
                        <code>{paymentRequest}</code>
                    </div>
                {:else}
                    <div id="bid" class="form-group">
                        <input id="bid-amount" name="bid-amount" type="number" class="form-field" bind:value={amount} />
                        <label class="form-label" for="bid-amount">Amount</label>
                    </div>
                    <div class="glowbutton glowbutton-bid mt-5" on:click|preventDefault={placeBid}></div>
                {/if}
            {/if}
        {/if}
    </div>
</div>
{/if}

{#if !$token}
    <Login />
{/if}

