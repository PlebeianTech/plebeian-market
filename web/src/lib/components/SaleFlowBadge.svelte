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
    <p class="my-4">
        Please send your donation amount of <AmountFormatter satsAmount={sale.amount} />.
    </p>
    <p class="text-2xl text-center mb-4">
        <AmountFormatter satsAmount={sale.amount} />
    </p>
    <p class="text-txl text-center mb-4">
        BTC {formatBTC(sale.amount)}
    </p>
    <QR qr={sale.address_qr} protocol="bitcoin" address={sale.address} />
{/if}