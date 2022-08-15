<script lang="ts">
    import { postBid } from "$lib/services/api";
    import { Info, token } from "../stores";
    import AmountFormatter, { AmountFormat } from './AmountFormatter.svelte';
    import QR from "./QR.svelte";

    export let auctionKey;
    export let amount;

    let paymentRequest = null;
    let paymentQr = null;

    function placeBid() {
        postBid($token, auctionKey, amount,
            (r, q, messages) => {
                paymentRequest = r;
                paymentQr = q;
                for (const message of messages) {
                    setTimeout(() => Info.set(message), 0);
                }
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
{:else}
    <div class="form-control w-full max-w-xs">
        <label class="label" for="bid-amount">
            <span class="label-text">Suggested bid</span>
        </label>
        <input bind:value={amount} type="number" name="bid-amount" id="bid-amount" class="input input-bordered w-full max-w-xs" />
        <label class="label" for="bid-amount">
            <span class="label-text"><AmountFormatter satsAmount={amount} format={AmountFormat.Usd} /></span>
            <span class="label-text">sats</span>
        </label>
    </div>
    <div class="w-full flex items-center justify-center">
        <div class="glowbutton glowbutton-bid mt-2" on:click|preventDefault={placeBid}></div>
    </div>
{/if}
</div>