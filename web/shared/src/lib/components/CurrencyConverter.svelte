<script lang="ts">
    import {convertCurrencies, getCurrencyInfo, getStandardCurrencyCode} from "$sharedLib/currencies";
    import {userChosenCurrency} from "$sharedLib/stores";

    export let amount: number;
    export let sourceCurrency: string;
    export let classStyle = "";
    export let originalClassStyle = "text-xs";

    let convertedSuccessfully = false;

    $: destinationCurrencyInfo = null;
    $: convertedAmount = null;

    async function convert() {
        convertedSuccessfully = false;

        destinationCurrencyInfo = getCurrencyInfo($userChosenCurrency);

        convertedAmount = await convertCurrencies(amount, sourceCurrency);
        if (convertedAmount) {
            convertedSuccessfully = true;
        }
    }

    $: if (amount && sourceCurrency && $userChosenCurrency) {
        convert();
    }
</script>

{#if !amount || !sourceCurrency}
    <p class="text-sm">{amount} {sourceCurrency}</p>
{:else}
    {#if !$userChosenCurrency || !destinationCurrencyInfo}
        <p>{amount} {sourceCurrency}</p>
    {:else}
        {#if convertedSuccessfully}
            <div>
                <p class="{classStyle}">{destinationCurrencyInfo.prefix}{convertedAmount}{destinationCurrencyInfo.suffix}</p>
                {#if getStandardCurrencyCode(sourceCurrency) !== getStandardCurrencyCode($userChosenCurrency)}
                    <p class="{originalClassStyle}">({amount} {sourceCurrency})</p>
                {/if}
            </div>
        {:else}
            <p>
                {amount} {sourceCurrency}
                <span class="loading loading-bars w-6"></span>
            </p>
        {/if}
    {/if}
{/if}
