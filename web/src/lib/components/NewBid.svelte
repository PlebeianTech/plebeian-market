<script lang="ts">
    import { postBid, putBuy, setLock } from "../services/api";
    import { token } from "../stores";
    import QR from "./QR.svelte";
    import AmountFormatter from "./AmountFormatter.svelte";
    import Countdown from "./Countdown.svelte";

    export let amount;
    export let auction;

    let paymentRequest = null;
    let paymentQr = null;
    let currentTime = new Date();

    function placeBid() {
        postBid($token, auction.key, amount,
            (r, q) => {
                paymentRequest = r;
                paymentQr = q;
            });
    }

    function buyListing() {
        putBuy($token, auction.key,
            (r, q) => {
                paymentRequest = r;
                paymentQr = q;
            });
    }

    function lockListing() {
        setLock($token, auction.key,
            () => {
            });
    }

    export function waitingSettlement() {
        return paymentRequest !== null;
    }

    export function reset() {
        paymentQr = paymentRequest = amount = null;
    }

    export function paymentConfirmed(r) {
        if (paymentRequest === r) {
            reset();
        }
    }
</script>

<div>
{#if paymentQr}
    <QR bind:qr={paymentQr} bind:lnurl={paymentRequest} />
    {#if auction.isInstantBuy()}
        <Countdown untilDate={new Date(currentTime.setMinutes(currentTime.getMinutes()+3))} />
    {/if}
{:else}
    <div class:hidden={auction.isInstantBuy()} class="form-control w-full max-w-xs">
        <label class="label" for="bid-amount">
            <span class="label-text">Suggested bid</span>
        </label>
        <input bind:value={amount} type="number" name="bid-amount" id="bid-amount" class="input input-bordered w-full max-w-xs" />
        <label class="label" for="bid-amount">
            <span class="label-text"></span>
            <span class="label-text">sats</span>
        </label>
    </div>
    <div class="w-full flex items-center justify-center">
        {#if auction.isInstantBuy()}
            <div class="glowbutton-buy glowbutton mt-2" on:click|preventDefault={lockListing, buyListing}></div>
        {:else}
            <div class="glowbutton-bid glowbutton mt-2" on:click|preventDefault={placeBid}></div>
        {/if}
    </div>
{/if}
</div>