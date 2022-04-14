<script>
    import dayjs from 'dayjs';
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
                        for (const bid of auction.bids) {
                            if (bid.payment_request === paymentRequest) {
                                paymentQr = paymentRequest = null;
                            }
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
    <p>From <Time timestamp={ auction.starts_at } format="dddd @ H:mm · MMMM D, YYYY" /> to <Time timestamp={ auction.ends_at } format="dddd @ H:mm · MMMM D, YYYY" /></p>
    <p><span>Minimum bid: { auction.minimum_bid }</span></p>
    <ul id="bids">
        {#each auction.bids as bid}
            <li>{bid.amount} (by {bid.bidder})</li>
        {/each}
    </ul>
{/if}

{#if $token}
    {#if auction}
        {#if auction.canceled}
            <div>Auction was canceled.</div>
        {:else if !auction.started}
            <div>Auction not started yet.</div>
        {:else if auction.ended}
            <div>Auction already ended.</div>
        {:else}
            <div id="bid">
                <div>
                    <input id="bid-amount" type="number" bind:value={amount} />
                </div>
                <div>
                    <button on:click|preventDefault={placeBid}>Place bid</button>
                </div>
            </div>
            {#if paymentQr}
                <div class="qr glow-box">
                    {@html paymentQr}
                    <code>{paymentRequest}</code>
                </div>
            {/if}
        {/if}
    {/if}
{:else}
    <Login />
{/if}

