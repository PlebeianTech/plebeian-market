<script lang="ts">
    import {getFiatCurrencyInfo} from "$sharedLib/currencies";
    import {currentFiatCurrency, fiatRates} from "$sharedLib/stores";

    export let satsAmount: number | null = null;
    export let useParentheses = true;
    export let classStyle = "";

    $: fiatCurrencyInfo = null;
    $: convertedAmount = null;

    $: if (satsAmount && $currentFiatCurrency && $fiatRates.has($currentFiatCurrency)) {
        fiatCurrencyInfo = getFiatCurrencyInfo($currentFiatCurrency);

        calculateFiatAmount($fiatRates.get($currentFiatCurrency).rate);
    }

    function calculateFiatAmount(fiatRate) {
        convertedAmount = satsAmount * fiatRate / 100000000;

        if (!isNaN(convertedAmount)) {
            if (convertedAmount > 1) {
                convertedAmount = convertedAmount.toFixed(2);
            } else if (convertedAmount > 99) {
                convertedAmount = convertedAmount.toFixed(0);
            } else {
                convertedAmount = convertedAmount.toFixed(4);
            }
        }
    }
</script>

{#if satsAmount && convertedAmount && fiatCurrencyInfo}
    <span class="{classStyle}">{#if useParentheses}({/if}{fiatCurrencyInfo.prefix}{convertedAmount}{fiatCurrencyInfo.suffix}{#if useParentheses}){/if}</span>
{/if}
