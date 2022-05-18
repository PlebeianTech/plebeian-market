<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { postBid, getAuction } from "../services/api";
    import { type Auction, nextBid } from "../types/auction";
    import { token, user } from "../stores";
    import BidList from "./BidList.svelte";
    import Carousel from "./Carousel.svelte";
    import Countdown from "./Countdown.svelte";
    import Login from "./Login.svelte";

    export let auctionKey = null;

    let auction: Auction | null = null;
    let bidCount = 0;
    let amount: number | null = null;
    let paymentRequest = null;
    let paymentQr = null;

    function placeBid() {
        postBid($token, auctionKey, amount,
            (r, q) => {
                paymentRequest = r;
                paymentQr = q;
            });
    }

    function refreshAuction() {
        getAuction($token, auctionKey,
            a => {
                auction = a;
                var maxBid = auction!.starting_bid;
                for (const bid of auction!.bids) {
                    if (bid.payment_request === paymentRequest) {
                        paymentQr = paymentRequest = amount = null;
                    }
                    if (bid.amount > maxBid) {
                        maxBid = bid.amount;
                    }
                }
                if (!amount || auction!.bids.length != bidCount) {
                    amount = nextBid(maxBid);
                }
                bidCount = auction!.bids.length;
                if (finalCountdown && finalCountdown.isLastMinute()) {
                    document.title = "LAST MINUTE";
                }
            });
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    let finalCountdown;

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

<svelte:head>
    <title>Auction</title>
</svelte:head>

{#if auction}
<div class="flex justify-center items-center">
    <div class="mt-2 w-3/5 rounded p-4">
        <h2 class="text-3xl">{auction.title}</h2>
        <p class="mt-4">{auction.description}</p>

        <Carousel photos={auction.media} />

        <p>
            {#if auction.start_date && auction.end_date}
                {#if !auction.started}
                    Auction starts <Countdown untilDate={new Date(auction.start_date)} />.
                {:else if auction.ended}
                    Auction ended.
                {:else}
                    <Countdown bind:this={finalCountdown} untilDate={new Date(auction.end_date)} />
                    {#if auction.started && !auction.reserve_bid_reached}
                        <p class="mt-2 w-full text-xl text-center">Reserve not met!</p>
                    {/if}
                {/if}
            {:else}
                {#if auction.is_mine}
                    Your auction is not running. Please go to <a class="link" href="/auctions">My Auctions</a> and click Start!
                {:else}
                    Keep calm, prepare your Lightning wallet and wait for the seller to start this auction.
                {/if}
            {/if}
        </p>
        <div class="mt-4 flex">
            <div class=w-1/2>
                {#if $token}
                    {#if $user && $user.twitterUsername !== null && auction.started && !auction.ended}
                        {#if paymentQr}
                            <div class="qr glowbox">
                                {@html paymentQr}
                                <span class="break-all text-xs">{paymentRequest}</span>
                            </div>
                        {:else}
                            <div class="form-control w-full max-w-xs">
                                {#if auction.end_date_extended}
                                    <h3 class="text-2xl text-warning">Time Extended</h3>
                                {/if}
                                <label class="label" for="bid-amount">
                                    <span class="label-text">Suggested bid</span>
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

            <div class="w-1/2">
                {#if auction.bids.length}
                    <div class="mt-2">
                        <BidList auction={auction} />
                    </div>
                {/if}
            </div>

        </div>
    </div>
</div>
{/if}