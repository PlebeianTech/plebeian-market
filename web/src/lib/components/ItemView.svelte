<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import SvelteMarkdown from 'svelte-markdown';
    import { MetaTags } from 'svelte-meta-tags';
    import { ErrorHandler, getItem, putAuctionFollow, type ILoader } from "$lib/services/api";
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
    import { page } from "$app/stores";
    import { getBaseUrl } from "$lib/utils";

    export let loader: ILoader;
    export let itemKey = null;
    export let serverLoadedItem: Listing;

    let bidButton: BidButton;

    let sale: Sale | null = null;

    let item: Item | null = null;
    let bidCount = 0;
    let amount: number | null = null;
    let firstUpdate = true;

    let tweetURL = null;

    function refreshItem() {
        getItem(loader, $token, itemKey,
            i => {
                item = i;
                if (!item) {
                    return;
                }

                if (item instanceof Auction) {
                    if (bidButton && bidButton.bidConfirmed && bidButton.waitingBidSettlement && bidButton.waitingBadgeSale && bidButton.resetBid) { // TODO: why are these checks needed? Typescript trying to be smart? Svelte acting stupid? Can we get rid of them?
                        for (const bid of item.bids) {
                            if (bid.payment_request !== null) {
                                // NB: payment_request being set on the Bid means this is *my* bid, which has been confirmed
                                bidButton.bidConfirmed(bid.payment_request);
                            }
                            if (amount && amount <= bid.amount && (bidButton.waitingBidSettlement() || bidButton.waitingBadgeSale())) {
                                Error.set("A higher bid just came in.");
                                bidButton.resetBid();
                            }
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

                tweetURL = 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(getBaseUrl() + 'auctions/' + item?.key) + '&text=' + item?.title;
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

<MetaTags
    title={serverLoadedItem?.title ?? "Plebeian Market item"}
    description={serverLoadedItem?.description ?? import.meta.env.VITE_PM_DESCRIPTION}
    openGraph={{
        site_name: "Plebeian Market",
        type: 'website',
        url: $page.url.href,
        title: serverLoadedItem?.title ?? "Plebeian Market item",
        description: serverLoadedItem?.description ?? import.meta.env.VITE_PM_DESCRIPTION,
        images: [{ url: serverLoadedItem && serverLoadedItem.media.length ? serverLoadedItem.media[0].url : "/images/logo.jpg" }],
    }}
    twitter={{
        site: import.meta.env.VITE_TWITTER_USER,
        handle: import.meta.env.VITE_TWITTER_USER,
        cardType: "summary_large_image",
        imageAlt: serverLoadedItem?.title ?? "Plebeian Market item",
    }}
/>

{#if item}
    <div class="lg:w-2/3 mx-auto p-2">
        {#if $user && item.is_mine && !item.started}
            <div class="alert alert-error shadow-lg mt-12 lg:w-2/3 mx-auto">
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
        {#if !item.is_mine}
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
        {/if}

        <div class="grid">
            <div class="py-20">
                <h2 class="lg:text-6xl text-3xl lg:w-1/2 mx-auto font-black text-center mt-2 mb-4 rounded-t py-1.5">{item.title}</h2>
                <!-- CONTENT -->
                <div class="grid lg:grid-cols-3 my-20">
                  <!-- LEFT  -->
                  <div class="lg:sticky top-24">
                    <!-- IMAGES -->
                    <div class="w-64">
                      <Gallery photos={item.media} />
                    </div>
                    <!-- DETAILS -->
                    <div>
                      <div class="">
                        <!-- <span class="flex text-1xl text-center mr-2 mb-4 mt-2 py-1.5 rounded-t">
                            <h3 class="mx-1">Auction Details</h3>
                        </span> -->

                        <div class="markdown-container mt-12">
                            <SvelteMarkdown source={item.description} />
                        </div>
                        {#if item.category !== Category.Time}
                            <p class="mt-4 ml-2">NOTE: Please allow for post and packaging.</p>
                        {/if}

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

                      <div class="grid">
                          {#if item.campaign_name !== null}
                              <div class="badge badge-primary mb-4"><a href="/campaigns/{item.campaign_key}">{item.campaign_name} campaign</a></div>
                          {/if}
                          <div class="grid place-content-start">
                            <Avatar account={item.seller} />
                          </div>

                          {#if item instanceof Auction}
                              <div class="form-control flex place-items-start">
                                  <label class="label cursor-pointer text-left">
                                      <span class="label-text mr-4">Follow auction</span>
                                      <input type="checkbox" on:click|preventDefault={followAuction} bind:checked={item.following} class="checkbox checkbox-primary checkbox-lg" />
                                  </label>
                              </div>
                          {/if}
                      </div>
                  </div>
                  </div>

                  <!-- BIDS -->
                  <div class="lg:col-span-2 p-5 border w-full border-gray-700/40 rounded">
                    {#if item.ended}
                        {#if item instanceof Auction}
                            <h3 class="text-2xl text-center my-2">
                                Auction ended
                            </h3>
                            {#if item.is_mine}
                                <div class="my-8 flex gap-2 items-center justify-center">
                                    {#if item.has_winner && item.winner}
                                        <span>The winner is</span>
                                        <Avatar account={item.winner} inline={true} />
                                    {:else}
                                        <span>The auction doesn't have a winner.</span>
                                    {/if}
                                </div>
                                {#if sale}
                                    {#if sale.state === SaleState.TX_DETECTED || sale.state === SaleState.TX_CONFIRMED}
                                        <p class="my-4 text-center w-full">Please contact the winner using <a class="link" href="https://twitter.com/direct_messages/create/{sale.buyer.twitterUsername}" target="_blank" rel="noreferrer">Twitter DM</a> to discuss further.</p>
                                        <div class="alert shadow-lg my-4" class:alert-warning={sale.state === SaleState.TX_DETECTED} class:alert-success={sale.state === SaleState.TX_CONFIRMED}>
                                            <div>
                                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                                <span>
                                                    TxID: <a class="link break-all" target="_blank" href="https://mempool.space/tx/{sale.txid}" rel="noreferrer">{sale.txid}</a>
                                                </span>
                                            </div>
                                        </div>
                                        {#if item.campaign_name !== null}
                                            <div class="text-center text-2xl my-8">
                                                <p>Note: all the money goes from the buyer <strong>directly to</strong></p>
                                                <div class="badge badge-primary my-4"><a href="/campaigns/{item.campaign_key}">{item.campaign_name} campaign</a></div>
                                            </div>
                                        {/if}
                                    {:else if sale.state === SaleState.EXPIRED}
                                        <div class="alert alert-error shadow-lg my-4">
                                            <div>
                                                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                <span>
                                                    {#if sale.txid !== null}
                                                        Unfortunately, the transaction did not confirm in time!
                                                        <br />
                                                        TxID: <a class="link break-all" target="_blank" href="https://mempool.space/tx/{sale.txid}" rel="noreferrer">{sale.txid}</a>
                                                    {:else}
                                                        We didn't find a corresponding transaction!
                                                    {/if}
                                                </span>
                                            </div>
                                        </div>
                                    {:else}
                                        <p class="text-center text-2xl my-4">Waiting for the payment</p>
                                    {/if}
                                {/if}
                            {/if}
                        {/if}
                    {/if}
                    {#if !item.is_mine && sale && sale.state !== SaleState.EXPIRED}
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
                                            Your auction is live! <br />

                                            <div class="text-xl text-center my-2 mt-10 mb-10">
                                                Now let your audience know!
                                                &nbsp;
                                                <a class="btn align-middle bg-blue-500 hover:bg-indigo-500" target="_blank" rel="noreferrer" href="{tweetURL}">
                                                    <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
                                                        <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                                                    </svg>
                                                    &nbsp;
                                                    Tweet
                                                </a>
                                            </div>
                                        {:else if item instanceof Listing}
                                            Your listing is live! <br />
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
                </div>
                <!-- BIDS END -->
            </div>
        </div>
    </div>
{/if}
