<script lang="ts">
    import { SaleState, type Sale } from "$lib/types/sale";
    import { formatBTC } from "$lib/utils";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import QR from "$lib/components/QR.svelte";

    export let sale: Sale;
</script>

<ul class="steps steps-vertical lg:steps-horizontal">
    <li class="step" class:step-primary={sale.state === SaleState.CONTRIBUTION_SETTLED || sale.state === SaleState.TX_DETECTED || sale.state === SaleState.TX_CONFIRMED}>
        <p class="text-left">Payment</p>
    </li>
    <li class="step" class:step-primary={sale.state === SaleState.TX_DETECTED || sale.state === SaleState.TX_CONFIRMED}>
        <p class="text-left">Confirmation</p>
    </li>
</ul>

{#if sale.state === SaleState.CONTRIBUTION_SETTLED}
    <h3 class="mt-4 text-2xl">Skin in the game</h3>
    <p class="mt-4">
        In order to bid over $500 we ask plebs for a 1-time fee, the equivalent of $50... this has two benefits:
    </p>
    <ul class="list-disc mt-2">
        <li>It shows that you are a committed participant</li>
        <li>It deters spam</li>
    </ul>
    <p class="mt-2">If you do this within a campaign, the money will go directly to that campaign! If you do this anywhere else on Plebeian Market, you will be enabling us to continue to develop this service.</p>
    <p class="mt-2">You will receive a badge for the campaign you have contributed to and/or also a Plebeian Market Player badge. These will be visible on your Market Stall and will contribute towards your reputation.</p>
    <p class="text-2xl text-center my-4">
        <AmountFormatter satsAmount={sale.amount} />
    </p>
    <p class="text-txl text-center mb-4">
        BTC {formatBTC(sale.amount)}
    </p>
    <QR qr={sale.qr} protocol="bitcoin" address={sale.address} />
{/if}