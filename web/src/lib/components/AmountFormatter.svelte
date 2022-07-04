<script>
    import { BTC2USD } from "../stores";
    import { sats2usd } from "../utils";

    export let amount;

    export let fiatFirst = false;

    function formatUSD(amount) {
        let usd = sats2usd(amount, $BTC2USD);
        if (usd) {
            return usd.toFixed(2);
        } else {
            return "";
        }
    }
</script>

{#if fiatFirst}
    <span title="{amount.toLocaleString('en') + " sats"}">{formatUSD(amount)}</span>
{:else}
    <span title="{formatUSD(amount) + " $"}">{amount.toLocaleString('en')}</span>
{/if}