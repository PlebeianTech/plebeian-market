<script lang="ts">
    import {convertCurrencies, getCurrencyInfo, getStandardCurrencyCode} from "$sharedLib/currencies";
    import {userChosenCurrency} from "$sharedLib/stores";

    export let amount: number;
    export let sourceCurrency: string;
    export let satsClassStyle = "";
    export let fiatClassStyle = "text-xs";
    export let showOnlySats = false;
    export let parenthesisOnFiat = true;

    let convertedSuccessfully = false;

    $: destinationCurrencyInfo = null;
    $: convertedAmount = null;
    $: satsAmount = null;

    async function convert() {
        convertedSuccessfully = false;

        destinationCurrencyInfo = getCurrencyInfo($userChosenCurrency);

        const convertedAmountObject = await convertCurrencies(amount, sourceCurrency);
        if (convertedAmountObject) {
            convertedAmount = convertedAmountObject.amount;
            satsAmount = convertedAmountObject.sats;
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
                <p class="{satsClassStyle} aamr-1">{satsAmount} sat</p>
                {#if !showOnlySats && getStandardCurrencyCode($userChosenCurrency) !== 'SAT'}
                    <p class="{fiatClassStyle}">{#if parenthesisOnFiat}({/if}{destinationCurrencyInfo.prefix}{convertedAmount}{destinationCurrencyInfo.suffix}{#if parenthesisOnFiat}){/if}</p>
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
