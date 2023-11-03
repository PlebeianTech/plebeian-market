<script lang="ts">
    import {getFiatRate, supportedFiatCurrencies} from "$sharedLib/currencies";
    import { currentFiatCurrency } from "$sharedLib/stores";
    import {onMount} from "svelte";

    export let classStyle = "hidden select-bordered select-info max-w-xs border rounded py-2 px-3";

    $: if ($currentFiatCurrency) {

        getFiatRate($currentFiatCurrency);
        localStorage.setItem('currentFiatCurrency', $currentFiatCurrency);
    }

    onMount(async () => {
        if (!$currentFiatCurrency) {
            $currentFiatCurrency = 'USD';
        }
    });
</script>

<select class="{classStyle}" bind:value={$currentFiatCurrency}>
    {#each supportedFiatCurrencies as fiatCurrency}
        <option value={fiatCurrency.symbol}>{fiatCurrency.name}</option>
    {/each}
</select>
