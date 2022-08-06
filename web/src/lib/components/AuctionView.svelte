<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import SvelteMarkdown from 'svelte-markdown';
    import { ErrorHandler, getAuction, putAuctionFollow } from "$lib/services/api";
    import { Error, Info, token, user } from "$lib/stores";
    import type { Auction } from "$lib/types/auction";
    import type { User } from "$lib/types/user";
    import Avatar from "$lib/components/Avatar.svelte";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import AuctionEndMessage from "$lib/components/AuctionEndMessage.svelte";
    import BidList from "$lib/components/BidList.svelte";
    import Countdown from "$lib/components/Countdown.svelte";
    import Gallery from "$lib/components/Gallery.svelte";
    import Login from "$lib/components/Login.svelte";
    import NewBid from "$lib/components/NewBid.svelte";

    export let auctionKey = null;

    let newBid: NewBid;

    let auction: Auction | null = null;
    let bidCount = 0;
    let amount: number | null = null;
    let firstUpdate = true;

    function refreshAuction() {
        getAuction($token, auctionKey,
        a => {
            auction = a;
            if (!auction) {
                return;
            }
            for (const bid of auction.bids) {
                if (newBid && bid.payment_request !== undefined) {
                    // NB: payment_request being set on the Bid means this is *my* bid, which has been confirmed
                    newBid.paymentConfirmed(bid.payment_request);
                }
                if (amount && amount <= bid.amount && newBid.waitingSettlement()) {
                    Error.set("A higher bid just came in.");
                    newBid.reset();
                }
            }

            if ((!amount && firstUpdate) || auction.bids.length != bidCount) {
                amount = auction.nextBid();
                firstUpdate = false;
            }
            bidCount = auction.bids.length;
            if (finalCountdown && finalCountdown.isLastMinute()) {
                document.title = `LAST MINUTE - ${auction.title} | Plebeian Market`;
            } else {
                document.title = `${auction.title} | Plebeian Market`;
            }
            if (auction.has_winner) {
                document.title = `Ended - ${auction.title} | Plebeian Market`;
                console.log("Auction ended!");
                // maybe we should eventually stopRefresh() here, but is seems risky for now, at least while still testing
            }
        },
        new ErrorHandler(false));
    }

    function onLogin(user: User | null) {
        if (user && user.twitter.username === null) {
            localStorage.setItem('initial-login-buyer', "1");
        }
    }

    function followAuction() {
        if (auction) {
            auction.following = !auction.following;
            putAuctionFollow($token, auction.key, auction.following,
                message => {
                    Info.set(message);
                });
        }
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
    <div>
        {#if $user && auction.is_mine && !auction.start_date && !auction.end_date}
            <div class="alert alert-error shadow-lg">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>
                        Your auction is not running. Please go to <a class="link" href="/stall/{$user.nym}">My stall</a> and click Start!
                    </span>
                </div>
            </div>
        {/if}
        <div class="grid lg:grid-cols-3 gap-4">
            <div class="p-5">
                <h2 class="text-3xl text-center mt-2 mb-4 md:mr-2 rounded-t bg-black/5 py-1.5">{auction.title}</h2>
                <div class="text-center mb-4">
                    by <Avatar account={auction.seller} />
                </div>
                <Gallery photos={auction.media} />
            </div>
            <div class="mr-4 p-5">
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
                            {#if $user && $user.twitter.username !== null && auction.started && !auction.ended}
                                <div class="flex justify-center items-center">
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
                        <Login {onLogin} />
                    {/if}
                {/if}
                {#if auction.start_date && auction.end_date}
                    {#if auction.started && !auction.ended}
                        <div class="py-5">
                            <Countdown bind:this={finalCountdown} untilDate={new Date(auction.end_date)} />
                        </div>
                    {/if}
                    {#if !auction.reserve_bid_reached}
                        <p class="my-3 w-full text-xl text-center">
                            Reserve not met!
                        </p>
                    {/if}
                {/if}
                {#if auction.bids.length}
                    <div class="mt-2">
                        <BidList {auction} />
                    </div>
                {:else}
                    {#if !auction.is_mine}
                        <p class="text-3xl text-center pt-24">Starting bid is <AmountFormatter satsAmount={auction.starting_bid} />.</p>
                        <p class="text-2xl text-center pt-2">Be the first to bid!</p>
                    {/if}
                {/if}
            </div>
            <div class="mr-5 p-5">
                <span class="flex text-1xl md:text-3xl text-center mr-2 mb-4 mt-2 py-1.5 bg-black/5 rounded-t">
                    <h3 class="mx-1">Product Details</h3>
                </span>
                <div class="form-control">
                    <label class="label cursor-pointer text-right">
                        <span class="label-text">Follow auction</span> 
                        <input type="checkbox" on:click|preventDefault={followAuction} bind:checked={auction.following} class="checkbox checkbox-primary checkbox-lg" />
                    </label>
                </div>
                <div class="markdown-container">
                    <SvelteMarkdown source={auction.description} />
                </div>
                {#if auction.shipping_from}
                    <p class="mt-4 ml-2">Shipping from {auction.shipping_from}</p>
                {/if}
                <p class="mt-4 ml-2">NOTE: Please allow for post and packaging. The seller can agree on this with you when you have won.</p>
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
        {#if auction.ended}
            <AuctionEndMessage {auction} />
        {/if}
    </div>
{/if}
