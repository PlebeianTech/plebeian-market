<script lang="ts">
    import {getFiatRate, supportedCurrencies} from "$sharedLib/currencies";
    import {userChosenCurrency} from "$sharedLib/stores";
    import {onMount} from "svelte";

    export let classStyle = "select-bordered select-info max-w-xs border rounded py-2 px-3";

    $: if ($userChosenCurrency) {
        getFiatRate($userChosenCurrency);
        localStorage.setItem('userChosenCurrency', $userChosenCurrency);
    }

    onMount(async () => {
        if (!$userChosenCurrency) {
            $userChosenCurrency = 'USD';
        }
    });
</script>

<select class="{classStyle}" bind:value={$userChosenCurrency}>
    {#each supportedCurrencies as currency}
        <option value={currency.symbol}>{currency.name}</option>
    {/each}
</select>
