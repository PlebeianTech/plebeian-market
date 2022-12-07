<script lang="ts">
    import { SaleState, type Sale } from "$lib/types/sale";
    import { formatBTC } from "$lib/utils";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import BadgeHelp from "$lib/components/BadgeHelp.svelte";
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
    <div class="mt-4">
        <BadgeHelp campaign_name={sale.campaign_name} />
    </div>

    <p class="text-2xl text-center my-4">
        <AmountFormatter satsAmount={sale.amount} />
    </p>

    <p class="text-txl text-center mb-4">
        BTC {formatBTC(sale.amount)}
    </p>

    <QR qr={sale.qr} protocol="bitcoin" address={sale.address} />
{/if}