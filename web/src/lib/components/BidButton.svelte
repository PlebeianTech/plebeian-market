<script lang="ts">
    import { ErrorHandler, postBid } from "$lib/services/api";
    import { Info, token } from "$lib/stores";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import QR from "$lib/components/QR.svelte";

    export let amount;

    export let item;

    let paymentRequest = null;
    let paymentQr = null;

    let waitingResponse = false;
    function placeBid() {
        waitingResponse = true;
        postBid($token, item.key, amount,
            (r, q, messages) => {
                paymentRequest = r;
                paymentQr = q;
                for (const message of messages) {
                    setTimeout(() => Info.set(message), 0);
                }
                waitingResponse = false;
            },
            new ErrorHandler(true, () => waitingResponse = false));
    }

    export function waitingBidSettlement() {
        return paymentRequest !== null;
    }

    export function resetBid() {
        paymentQr = paymentRequest = amount = null;
    }

    export function bidConfirmed(r) {
        if (paymentRequest === r) {
            resetBid();
        }
    }
</script>

<div>
    {#if paymentQr}
        <QR qr={paymentQr} protocol="lightning" address={paymentRequest} />
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
            {#if waitingResponse}
                <button class="btn" disabled>Bid</button>
            {:else}
                <div class="glowbutton glowbutton-bid mt-2" on:click|preventDefault={placeBid}></div>
            {/if}
        </div>
    {/if}
</div>