<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import { getAuction } from "../services/api";
    import { type Auction, nextBid } from "../types/auction";
    import { token, user } from "../stores";
    import AuctionEndMessage from "./AuctionEndMessage.svelte";
    import BidList from "./BidList.svelte";
    import Gallery from "./Gallery.svelte";
    import Carousel from "./Carousel.svelte";
    import NewBid from "./NewBid.svelte";
    import Countdown from "./Countdown.svelte";
    import Login from "./Login.svelte";

    export let auctionKey = null;

    let newBid: NewBid;

    let auction: Auction | null = null;
    let bidCount = 0;
    let amount: number | null = null;

    function refreshAuction() {
        getAuction($token, auctionKey,
        a => {
            auction = a;
            // TODO: maybe maxBid and nextBid should go to an Auction class
            var maxBid = auction!.starting_bid;
            for (const bid of auction!.bids) {
                if (newBid && bid.payment_request !== undefined) {
                    newBid.paymentConfirmed(bid.payment_request);
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
                document.title = `LAST MINUTE - ${auction!.title} | Plebeian Market`;
            } else {
                document.title = `${auction!.title} | Plebeian Market`;
            }
            if (auction!.has_winner) {
                document.title = `Ended - ${auction!.title} | Plebeian Market`;
                console.log("Auction ended!");
                // maybe we should eventually stopRefresh() here, but is seems risky for now, at least while still testing
            }
        });
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    let finalCountdown;

    onMount(async () => {
        refreshAuction();
        interval = setInterval(refreshAuction, 1000);
    });

    function stopRefresh() {
        if (interval) {
            clearInterval(interval);
            interval = undefined;
        }
    }

    onDestroy(stopRefresh);
</script>

<svelte:head>
    <title>Auction</title>
</svelte:head>

{#if auction}
    <div class="flex justify-center items-center">
        <div class="mt-2 w-4/5 rounded p-4">
            {#if auction.is_mine && !auction.start_date && !auction.end_date}
                <div class="alert alert-error shadow-lg">
                    <div>
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>
                            Your auction is not running. Please go to <a class="link" href="/auctions">My Auctions</a> and click Start!
                        </span>
                    </div>
                </div>
            {/if}

            <div class="mt-4 lg:flex">
                <div class="lg:w-1/3">
                    <h2 class="text-3xl text-center mb-4">{auction.title}</h2>
                    <div class="hidden lg:grid">
                    <Gallery photos={auction.media} />
                    </div>
                    <div class="lg:hidden">
                    <Carousel photos={auction.media} />
                    </div>
                </div>
                <div class="lg:w-1/2">
                    {#if auction.bids.length}
                        <div class="mt-2">
                            <BidList {auction} />
                        </div>
                    {:else}
                        <p class="text-3xl text-center pt-24">Current Bid</p>
                        <p class="text-2xl text-center pt-2 pb-24">0 Sats</p>
                    {/if}
                    {#if auction.start_date && auction.end_date}
                        {#if auction.started && !auction.ended}
                            <Countdown bind:this={finalCountdown} untilDate={new Date(auction.end_date)} />
                            {#if !auction.reserve_bid_reached}
                                <p class="mt-2 w-full text-xl text-center">
                                    Reserve not met!
                                </p>
                            {/if}
                        {/if}
                    {/if}
                </div>
                <div class="lg:w-1/3">
                    <h3 class="text-3xl mb-4 ml-2">Product Details:</h3>
                    <p class="mt-4 ml-2">{auction.description}</p>
                    {#if auction.shipping_from}
                        <p class="mt-4 ml-2">Shipping from {auction.shipping_from}</p>
                    {/if}
                    <p class="mt-4 ml-2">
                        {#if auction.start_date && auction.end_date}
                            {#if !auction.started}
                                Auction starts <Countdown untilDate={new Date(auction.start_date)} />.
                            {:else if auction.ended}
                                Auction ended.
                            {/if}
                        {:else if !auction.is_mine}
                            Keep calm, prepare your Lightning wallet and wait for the seller to start this auction.
                        {/if}
                    </p>
                </div>
            </div>

            <div class="mt-4">

                {#if !auction.ended}
                    {#if auction.end_date_extended}
                        <h3 class="text-2xl text-center text-warning my-2">
                            Time Extended
                        </h3>
                    {/if}
                    {#if $token && $user}
                        {#if !auction.is_mine}
                            {#if !auction.bids.length}
                                <p class="text-center pt-12">Place your bid below</p>
                            {/if}
                            {#if $user && $user.twitterUsername !== null && auction.started && !auction.ended}
                                <div class="mt-4 flex justify-center items-center">
                                    <NewBid bind:this={newBid} auctionKey={auction.key} bind:amount />
                                </div>
                            {/if}
                        {:else}
                            {#if auction.started}
                                <p class="text-center pt-24">Your auction is running &#x1FA99; &#x1F528; &#x1F4B0;</p>
                            {/if}
                        {/if}
                    {:else}
                        {#if !auction.bids.length}
                            <p class="text-center pt-24">Login below to place a bid</p>
                        {/if}
                        <Login />
                    {/if}
                {/if}
            </div>

            {#if auction.ended}
                <AuctionEndMessage {auction} />
            {/if}
        </div>
    </div>
{/if}
