<script>
    import { onDestroy, onMount } from 'svelte';
    import Carousel from 'svelte-carousel';
    import Time from 'svelte-time';
    import { fromJson, fetchAPI } from "../common.js";
    import { token, TwitterUsername } from '../stores.js';
    import Loading from '../Loading.svelte';
    import Login from '../Login.svelte';
    import Profile from '../Profile.svelte';

    let isLoading = false;

    let selected = 'auction';

    export let key;
    if (window.location.hash.substring(1).startsWith('plebeian-auction-')) {
        key = window.location.hash.substring(1 + 'plebeian-auction-'.length);
    }

    let auction = null;
    let bidCount = 0;
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
                        setTimeout(refreshAuction, 1000);
                    });
                }
            }
        );
    }

    onMount(async () => { refreshAuction() });

    const unsubscribe = token.subscribe(tokenValue => {
        if (!tokenValue) {
            return;
        }
        isLoading = true;
        fetchAPI("/users/me", 'GET', tokenValue, null,
            (response) => {
                isLoading = false;
                if (response.status === 200) {
                    response.json().then(data => {
                        TwitterUsername.set(data.user.twitter_username);
                        if ($TwitterUsername === null) {
                            selected = 'profile';
                        }
                    });
                }
            });
    });
	onDestroy(unsubscribe);

    token.set(sessionStorage.getItem('token'));
</script>

{#if auction}
<div class="flex justify-center items-center">
    <div class="mt-2 w-3/5 bg-gray-900 rounded p-4">
        <button on:click={() => { if ($token) { selected = 'profile' }}} type="button" class="float-right flex mr-3 text-sm bg-gray-800 rounded-full md:mr-0 focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600" aria-expanded="false">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
            <svg class="hidden w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
        </button>
        {#if selected === 'auction'}
            <h2 class="text-zinc-300 text-3xl">{auction.title}</h2>
            <p class="text-zinc-300">{auction.description}</p>
            <Carousel>
                {#each auction.media as photo}
                    <div class="flex justify-center">
                        <img src={photo.url} alt="Auctioned object" />
                    </div>
                {/each}
            </Carousel>
            {#if auction.canceled}
                <p class="text-zinc-300">This auction was canceled.</p>
            {:else if auction.start_date}
                {#if !auction.started}
                    <p class="text-zinc-300">Auction starts <Time live relative timestamp={auction.start_date} />.</p>
                {:else if auction.ended}
                    <p class="text-zinc-300">Auction ended <Time live relative timestamp={auction.end_date} />.</p>
                {:else}
                    <p class="text-zinc-300"><Time timestamp={auction.start_date} format="dddd MMMM D, H:mm" /> - <Time timestamp={auction.end_date} format="dddd MMMM D, H:mm - YYYY" /></p>
                {/if}
            {:else}
                <p class="text-zinc-300">Keep calm, prepare your Lightning wallet and wait for the seller to start this auction.</p>
            {/if}
            <p class="text-zinc-300"><span>Starting bid: {auction.starting_bid}</span></p>
            <ul id="bids" class="text-zinc-300">
                {#each auction.bids as bid}
                    <li>{bid.amount} (by {bid.bidder})</li>
                {/each}
            </ul>
            {#if $token}
                {#if isLoading}
                    <Loading />
                {:else}
                    {#if $TwitterUsername !== null && auction.started && !auction.ended && !auction.canceled}
                        {#if paymentQr}
                            <div class="qr glowbox">
                                {@html paymentQr}
                                <span class="break-all text-xs">{paymentRequest}</span>
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
            {/if}
        {:else if selected === 'profile'}
            <Profile onSave={() => selected = 'auction'} updateContributionPercent={false} />
        {/if}
    </div>
</div>
{/if}

{#if !$token}
    <Login />
{/if}

