<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { fetchAPI } from "../services/api";
    import { fromJson, type Auction } from "../types/auction";
    import { token, user } from "../stores";
    import Countdown from "./Countdown.svelte";
    import Login from "./Login.svelte";

    export let auctionKey = null;

    let auction: Auction | null = null;
    let bidCount = 0;
    let amount: number | null = null;
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
        fetchAPI(`/auctions/${auctionKey}/bids`, 'POST', $token,
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
        fetchAPI(`/auctions/${auctionKey}`, 'GET', $token,
            null,
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        auction = fromJson(data.auction);
                        var maxBid = auction.starting_bid;
                        for (const bid of auction.bids) {
                            if (bid.payment_request === paymentRequest) {
                                paymentQr = paymentRequest = amount = null;
                            }
                            if (bid.amount > maxBid) {
                                maxBid = bid.amount;
                            }
                        }
                        if (!amount || auction.bids.length != bidCount) {
                            amount = nextBid(maxBid);
                        }
                        bidCount = auction.bids.length;
                    });
                }
            }
        );
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    onMount(async () => {
        refreshAuction();
        interval = setInterval(refreshAuction, 1000);
    });

    onDestroy(() => {
        if (interval) {
            clearInterval(interval);
            interval = undefined;
        }
    });
</script>

{#if auction}
<div class="flex justify-center items-center">
    <div class="mt-2 w-3/5 rounded p-4">
        <h2 class="text-3xl">{auction.title}</h2>
        <p>{auction.description}</p>
        <div class="carousel w-full">
            {#each auction.media as photo, i}
                <div id="{photo.twitter_media_key}" class="carousel-item w-full">
                    <img src={photo.url} alt="Auctioned object" />
                </div>
            {/each}
        </div>
        <div class="flex justify-center w-full py-2 gap-2">
            {#each auction.media as photo, i}
                <a href="#{photo.twitter_media_key}" class="btn btn-xs">{i + 1}</a>
            {/each}
        </div>
        {#if auction.start_date && auction.end_date}
            {#if !auction.started}
                <p>Auction starts <Countdown untilDate={new Date(auction.start_date)} />.</p>
            {:else if auction.ended}
                <p>Auction ended.</p>
            {:else}
                <Countdown untilDate={new Date(auction.end_date)} />
            {/if}
        {:else}
            <p>Keep calm, prepare your Lightning wallet and wait for the seller to start this auction.</p>
        {/if}
        <ul id="bids">
            {#each auction.bids as bid}
            <li>
                <div class="avatar" class:verified={bid.twitter_username_verified}>
                    <div class="w-8 rounded-full">
                        <img src={bid.twitter_profile_image_url} title={bid.twitter_username} alt={bid.twitter_username} />
                    </div>
                </div>
                {bid.amount} sats
            </li>
            {/each}
        </ul>
        {#if $token}
            {#if $user && $user.twitterUsername !== null && auction.started && !auction.ended}
                {#if paymentQr}
                    <div class="qr glowbox">
                        {@html paymentQr}
                        <span class="break-all text-xs">{paymentRequest}</span>
                    </div>
                {:else}
                    <div class="form-control w-full max-w-xs">
                        <label class="label" for="bid-amount">
                            <span class="label-text">Amount</span>
                        </label>
                        <input bind:value={amount} type="number" name="bid-amount" id="bid-amount" class="input input-bordered w-full max-w-xs" />
                        <label class="label" for="bid-amount">
                            <span class="label-text"></span>
                            <span class="label-text">sats</span>
                        </label>
                    </div>
                    <div class="glowbutton glowbutton-bid mt-5" on:click|preventDefault={placeBid}></div>
                {/if}
            {/if}
        {:else}
            <span>To start bidding, log in by scanning the QR code with your Lightning wallet.</span>
            <Login />
        {/if}
    </div>
</div>
{/if}