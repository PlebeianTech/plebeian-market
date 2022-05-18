<script lang="ts">
    import { postBid } from "../services/api";
    import { token } from "../stores";

    export let auctionKey;
    export let amount;

    let paymentRequest = null;
    let paymentQr = null;

    function placeBid() {
        postBid($token, auctionKey, amount,
            (r, q) => {
                paymentRequest = r;
                paymentQr = q;
            });
    }

    export function paymentConfirmed(r) {
        if (paymentRequest === r) {
            paymentQr = paymentRequest = amount = null;
        }
    }
</script>

{#if paymentQr}
    <div class="qr glowbox">
        {@html paymentQr}
        <span class="break-all text-xs">{paymentRequest}</span>
    </div>
{:else}
    <div class="form-control w-full max-w-xs">
        <label class="label" for="bid-amount">
            <span class="label-text">Suggested bid</span>
        </label>
        <input bind:value={amount} type="number" name="bid-amount" id="bid-amount" class="input input-bordered w-full max-w-xs" />
        <label class="label" for="bid-amount">
            <span class="label-text"></span>
            <span class="label-text">sats</span>
        </label>
    </div>
    <div class="glowbutton glowbutton-bid mt-5" on:click|preventDefault={placeBid}></div>
{/if}