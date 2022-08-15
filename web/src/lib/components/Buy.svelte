<script lang="ts">
    import { putBuy } from "$lib/services/api";
    import { Info, token } from "$lib/stores";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import QR from "$lib/components/QR.svelte";

    export let listingKey;

    let contributionAmount = null;
    let contributionPaymentRequest = null;
    let contributionPaymentQr = null;
    let amount = null;
    let address = null;
    let addressQr = null;

    function buy() {
        putBuy($token, listingKey,
            (ca, cr, cqr, a, addr, aqr, messages) => {
                contributionAmount = ca;
                contributionPaymentRequest = cr;
                contributionPaymentQr = cqr;
                amount = a;
                address = addr;
                addressQr = aqr;
                for (const message of messages) {
                    setTimeout(() => Info.set(message), 0);
                }
            });
    }

    export function waitingSettlement() {
        return contributionPaymentRequest !== null || address !== null;
    }

    export function resetContribution() {
        contributionAmount = contributionPaymentQr = contributionPaymentRequest = null;
    }

    export function contributionPaymentConfirmed(r) {
        if (contributionPaymentRequest === r) {
            resetContribution();
        }
    }

    export function reset() {
        amount = address = addressQr = null;
    }

    export function paymentConfirmed(a) {
        if (address === a) {
            reset();
        }
    }
</script>

<div>
{#if contributionPaymentQr}
    <p>The seller wishes to donate <AmountFormatter satsAmount={contributionAmount} /> sats out of the total price to Plebeian Technology. Please send the amount using the QR code below!</p>
    <QR bind:qr={contributionPaymentQr} bind:lnurl={contributionPaymentRequest} />
{:else if address}
    <p>Please send the remaining amount of <AmountFormatter satsAmount={amount} /> sats directly to the seller!</p>
    <QR bind:qr={addressQr} bind:lnurl={address} />
{:else}
    <div class="w-full flex items-center justify-center">
        <div class="glowbutton glowbutton-buy mt-2" on:click|preventDefault={buy}></div>
    </div>
{/if}
</div>