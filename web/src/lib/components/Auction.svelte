<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { getAuction } from "../services/api";
    import { type Auction, nextBid } from "../types/auction";
    import { token, user } from "../stores";
    import BidList from "./BidList.svelte";
    import NewBid from "./NewBid.svelte";
    import Carousel from "./Carousel.svelte";
    import Countdown from "./Countdown.svelte";
    import Login from "./Login.svelte";

    export let auctionKey = null;

    let newBid : NewBid;

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
    <div class="mt-2 w-4/5 rounded p-4">
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
            <div class="w-1/2 mr-10">
                {#if !auction.ended && auction.end_date_extended}
                    <h3 class="text-2xl text-warning mb-2">Time Extended</h3>
                {/if}
                {#if $token}
                    {#if $user && $user.twitterUsername !== null && auction.started && !auction.ended}
                        <NewBid bind:this={newBid} auctionKey={auction.key} bind:amount={amount} />
                    {/if}
                    {#if auction.ended}
                        {#if auction.is_lost}
                            <p class="my-4">
                                Unfortunately, you were outbid.
                            </p>
                        {:else if auction.is_won}
                            <p class="my-4">
                                Thank you for your contribution! Please keep in touch with the seller to discuss details about the payment and delivery.
                            </p>
                            <div class="flex items-center justify-center">
                                <div class="avatar">
                                    <div class="w-24 rounded-xl">
                                        <img src={auction.seller_twitter_profile_image_url} alt="Avatar" />
                                    </div>
                                </div>
                                <p class="text-5xl ml-5"><a class="link" href="https://twitter.com/{auction.seller_twitter_username}" target="_blank">@{auction.seller_twitter_username}</a></p>
                            </div>
                        {:else if auction.contribution_amount}
                            <p class="my-4">
                                The seller has decided to donate {auction.contribution_amount} sats out of the winning bid to Plebeian Technology.
                                Please send the amount using the QR code below!
                            </p>
                            <div class="qr glowbox">
                                {@html auction.contribution_qr}
                                <span class="break-all text-xs">{auction.contribution_payment_request}</span>
                            </div>
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