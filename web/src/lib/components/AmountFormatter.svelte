<script context="module" lang="ts">
    export enum AmountFormat {
        Sats,
        Usd,
        SatsAndUsd
    }
</script>

<script lang="ts">
    import { BTC2USD } from "../stores";
    import { sats2usd } from "../utils";

    export let satsAmount;
    export let format: AmountFormat = AmountFormat.SatsAndUsd;
    export let newline: boolean = false;

    function formatUSD(satsAmount) {
        let usd = sats2usd(satsAmount, $BTC2USD);
        if (usd !== null) {
            return usd.toFixed(2);
        } else {
            return "";
        }
    }
</script>

{#if format === AmountFormat.Sats || format === AmountFormat.SatsAndUsd}
    <span>{satsAmount.toLocaleString('en')} sats</span>
{/if}
{#if format === AmountFormat.Usd || format === AmountFormat.SatsAndUsd}
    {#if $BTC2USD}
        {#if format === AmountFormat.SatsAndUsd && newline}
            <br />
        {/if}
        (<span>${formatUSD(satsAmount)}</span>)
    {/if}
{/if}