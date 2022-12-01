<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import SvelteMarkdown from 'svelte-markdown';
    import { ErrorHandler, getItem, postBid, putAuctionFollow, type ILoader } from "$lib/services/api";
    import { Error, Info, token, user } from "$lib/stores";
    import { Category, type Item } from "$lib/types/item";
    import { Auction } from "$lib/types/auction";
    import { Listing } from "$lib/types/listing";
    import { SaleState, type Sale } from "$lib/types/sale";
    import type { User } from "$lib/types/user";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import Avatar from "$lib/components/Avatar.svelte";
    import BidButton from "$lib/components/BidButton.svelte";
    import BidList from "$lib/components/BidList.svelte";
    import BuyButton from "$lib/components/BuyButton.svelte";
    import Countdown from "$lib/components/Countdown.svelte";
    import Gallery from "$lib/components/Gallery.svelte";
    import Login from "$lib/components/Login.svelte";
    import SaleFlow from "$lib/components/SaleFlow.svelte";

    export let loader: ILoader;
    export let itemKey = null;

    let bidButton: BidButton;

    let sale: Sale | null = null;

    let item: Item | null = null;
    let bidCount = 0;
    let amount: number | null = null;
    let firstUpdate = true;

    function refreshItem() {
        getItem(loader, $token, itemKey,
            i => {
                item = i;
                if (!item) {
                    return;
                }

                if (item instanceof Auction) {
                    for (const bid of item.bids) {
                        if (bidButton && bid.payment_request !== null) {
                            // NB: payment_request being set on the Bid means this is *my* bid, which has been confirmed
                            bidButton.bidConfirmed(bid.payment_request);
                        }
                        if (amount && amount <= bid.amount && bidButton.waitingBidSettlement()) {
                            Error.set("A higher bid just came in.");
                            bidButton.resetBid();
                        }
                    }

                    if ((!amount && firstUpdate) || item.bids.length != bidCount) {
                        amount = item.nextBid();
                        firstUpdate = false;
                    }
                    bidCount = item.bids.length;
                    if (finalCountdown && finalCountdown.isLastMinute()) {
                        document.title = `LAST MINUTE - ${item.title} | Plebeian Market`;
                    } else {
                        document.title = `${item.title} | Plebeian Market`;
                    }
                    if (item.has_winner !== null) {
                        document.title = `Ended - ${item.title} | Plebeian Market`;
                        console.log("Auction ended!");
                        // maybe we should eventually stopRefresh() here, but is seems risky for now, at least while still testing
                    }
                } else if (item instanceof Listing) {
                    document.title = `${item.title} | Plebeian Market`;
                }

                var last_sale = item.sales.slice(-1).pop();
                if (last_sale) {
                    sale = last_sale;
                }
            },
            new ErrorHandler(false));
    }

    function onLogin(user: User | null) {
        if (user && user.nym === null) {
            localStorage.setItem('initial-login-buyer', "1");
        }
    }

    function followAuction() {
        if (item instanceof Auction) {
            let auction = item;
            if (auction) {
                auction.following = !auction.following;
                putAuctionFollow($token, auction.key, auction.following,
                    message => {
                        Info.set(message);
                    });
            }
        }
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    let finalCountdown;

    onMount(async () => {
        refreshItem();
        interval = setInterval(refreshItem, 1000);
    });

    function stopRefresh() {
        if (interval) {
            clearInterval(interval);
            interval = undefined;
        }
    }

    onDestroy(stopRefresh);
</script>

{#if item}
    <div>
        {#if $user && item.is_mine && !item.started}
            <div class="alert alert-error shadow-lg">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>
                        Your sale is not active. Please go to <a class="link" href="/stall/{$user.nym}#item-{item.key}">My stall</a> and click Start!
                    </span>
                </div>
            </div>
        {/if}
        {#if sale && sale.state === SaleState.EXPIRED}
            <div class="alert alert-error shadow-lg">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>
                        Sale expired. The transaction was not confirmed in time.
                    </span>
                </div>
            </div>
        {:else if sale && sale.state === SaleState.TX_CONFIRMED}
            <div class="alert alert-success shadow-lg">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>
                        Your payment has been confirmed!
                    </span>
                </div>
            </div>
        {/if}
        <div class="grid lg:grid-cols-3 gap-4">
            <div class="p-5">
                <h2 class="text-3xl text-center mt-2 mb-4 md:mr-2 rounded-t bg-black/5 py-1.5">{item.title}</h2>
                <div class="text-center mb-4">
                    {#if item.campaign_name !== null}
                        <div class="badge badge-primary mb-4"><a href="/campaigns/{item.campaign_key}">{item.campaign_name} campaign</a></div>
                    {/if}
                    <Avatar account={item.seller} />
                </div>
                <Gallery photos={item.media} />
            </div>
            <div class="mr-4 p-5">
                {#if item.ended}
                    {#if item instanceof Auction}
                        <h3 class="text-2xl text-center my-2">
                            Auction ended
                        </h3>
                    {/if}
                {/if}
                {#if sale && sale.state !== SaleState.EXPIRED}
                    <SaleFlow bind:item={item} bind:sale={sale} />
                {/if}
                {#if !item.ended}
                    {#if item instanceof Auction && item.end_date_extended}
                        <h3 class="text-2xl text-center text-warning my-2">
                            Time Extended
                        </h3>
                    {/if}
                    {#if $token && $user}
                        {#if !item.is_mine}
                            {#if $user.nym !== null && item.started}
                                {#if !item.ended}
                                    {#if item instanceof Auction}
                                        {#if !item.bids.length}
                                            <p class="text-center pt-12 mb-4">Place your bid below</p>
                                        {/if}
                                        <div class="flex justify-center items-center">
                                            <BidButton auction={item} bind:amount bind:this={bidButton} />
                                        </div>
                                    {:else if item instanceof Listing}
                                        {#if !sale || sale.state === SaleState.TX_CONFIRMED || sale.state === SaleState.EXPIRED}
                                            <div class="mt-8 flex justify-center items-center">
                                                <BuyButton {item} onSale={(s) => {sale = s;}} />
                                            </div>
                                        {/if}
                                    {/if}
                                {/if}
                            {/if}
                        {:else}
                            {#if item.started}
                                <p class="text-4xl text-center pt-24">
                                    {#if item instanceof Auction}
                                        Your auction is active <br /> &#x1FA99; &#x1F528; &#x1F4B0;
                                    {:else if item instanceof Listing}
                                        Your listing is active <br /> &#x1FA99; &#x1F528; &#x1F4B0;
                                        <br />
                                        Note: You can still edit it, by going to <a class="link" href="/stall/{$user.nym}">My stall</a>!
                                    {/if}
                                </p>
                            {/if}
                        {/if}
                    {:else}
                        {#if item instanceof Auction && !item.bids.length}
                            <p class="text-center pt-24">Login below to place a bid!</p>
                        {:else if item instanceof Listing}
                            <p class="text-center pt-24">Login below to buy this item for <AmountFormatter usdAmount={item.price_usd} />!</p>
                        {/if}
                        <Login {onLogin} />
                    {/if}
                {:else} <!-- item.ended -->
                    {#if item instanceof Listing}
                        <h3 class="text-2xl text-center my-2">
                            Sold out
                        </h3>
                    {/if}
                {/if}
                {#if item instanceof Auction}
                    {#if item.start_date && item.end_date}
                        {#if item.started && !item.ended}
                            <div class="py-5">
                                <Countdown bind:this={finalCountdown} untilDate={new Date(item.end_date)} />
                            </div>
                        {/if}
                        {#if !item.reserve_bid_reached}
                            <p class="my-3 w-full text-xl text-center">
                                Reserve not met!
                            </p>
                        {/if}
                    {/if}
                    {#if item.bids.length}
                        <div class="mt-2">
                            <BidList auction={item} />
                        </div>
                    {:else}
                        {#if !item.is_mine}
                            <p class="text-3xl text-center pt-24">Starting bid is <AmountFormatter satsAmount={item.starting_bid} />.</p>
                            <p class="text-2xl text-center pt-2">Be the first to bid!</p>
                        {/if}
                    {/if}
                {/if}
            </div>
            <div class="mr-5 p-5">
                <span class="flex text-1xl md:text-3xl text-center mr-2 mb-4 mt-2 py-1.5 rounded-t">
                    <h3 class="mx-1">Product Details</h3>
                </span>
                {#if item instanceof Auction}
                    <div class="form-control">
                        <label class="label cursor-pointer text-right">
                            <span class="label-text">Follow auction</span> 
                            <input type="checkbox" on:click|preventDefault={followAuction} bind:checked={item.following} class="checkbox checkbox-primary checkbox-lg" />
                        </label>
                    </div>
                {/if}
                <div class="markdown-container">
                    <SvelteMarkdown source={item.description} />
                </div>
                {#if item.category !== Category.Time}
                    <p class="mt-4 ml-2">NOTE: Please allow for post and packaging.</p>
                {/if}
                <div class="divider"></div>
                {#if item.shipping_from}
                    <h3 class="text-1xl md:text-3xl mt-4 ml-2">Shipping from {item.shipping_from}</h3>
                {/if}
                {#if item.shipping_domestic_usd}
                    <p class="mt-4 ml-2">Shipping (domestic): ~<AmountFormatter usdAmount={item.shipping_domestic_usd} /></p>
                {/if}
                {#if item.shipping_worldwide_usd}
                    <p class="mt-4 ml-2">Shipping (worldwide): ~<AmountFormatter usdAmount={item.shipping_worldwide_usd} /></p>
                {/if}
                <p class="mt-4 ml-2">
                    {#if item instanceof Auction}
                        {#if item.start_date && item.end_date}
                            {#if !item.started}
                                Auction starts <Countdown untilDate={new Date(item.start_date)} />.
                            {:else if item.ended}
                                Auction ended.
                            {/if}
                        {:else if !item.is_mine}
                            Keep calm, prepare your wallet and wait for the seller to start this auction.
                        {/if}
                    {/if}
                </p>
            </div>
        </div>
    </div>
{/if}
