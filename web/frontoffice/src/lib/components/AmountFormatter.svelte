<script context="module" lang="ts">
    export enum AmountFormat {
        Sats,
        Usd,
        SatsAndUsd
    }
</script>

<script lang="ts">
    import { BTC2USD } from "$lib/stores";
    import { sats2usd, usd2sats } from "$sharedLib/utils";

    export let satsAmount: number | null = null;
    export let usdAmount: number | null = null;
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

    function formatSats(usdAmount) {
        let sats = usd2sats(usdAmount, $BTC2USD);
        if (sats !== null) {
            return sats.toFixed();
        } else {
            return "";
        }
    }
</script>

{#if format === AmountFormat.Sats || format === AmountFormat.SatsAndUsd}
    {#if satsAmount !== null}
        <span>{satsAmount.toLocaleString('en')} sats</span>
    {:else if usdAmount !== null}
        {#if $BTC2USD}
            <span>{formatSats(usdAmount)} sats</span>
        {/if}
    {/if}
{/if}
{#if format === AmountFormat.Usd || format === AmountFormat.SatsAndUsd}
    {#if satsAmount !== null}
        {#if $BTC2USD}
            {#if format === AmountFormat.SatsAndUsd && newline}
                <br />
            {/if}
            (<span>${formatUSD(satsAmount)}</span>)
        {/if}
    {:else if usdAmount !== null}
        {#if format === AmountFormat.SatsAndUsd}
            (<span>${usdAmount.toFixed(2)}</span>)
        {:else}
            <span>${usdAmount.toFixed(2)}</span>
        {/if}
    {/if}
{/if}
