<script lang="ts">
    import { ErrorHandler, buyListing } from "$lib/services/api";
    import { token } from "$lib/stores";
    import type { Sale } from "$lib/types/sale";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";

    export let item;

    export let onSale: (s: Sale) => void = (s: Sale) => { };

    let waitingResponse = false;
    function buy() {
        waitingResponse = true;
        buyListing($token, item.key,
            (sale) => {
                onSale(sale);
                waitingResponse = false;
            },
            new ErrorHandler(true, () => waitingResponse = false));
    }
</script>

<div>
    {#if waitingResponse}
        <button class="btn" disabled>Buy</button>
    {:else}
        <p class="text-3xl text-center pt-12">Price: ~<AmountFormatter usdAmount={item.price_usd} /></p>
        <p class="text-3xl text-center pt-12">{item.available_quantity} items available</p>
        <div class="w-full flex items-center justify-center mt-4">
            <button class="btn btn-primary mt-2" on:click|preventDefault={buy} on:keypress={buy}>Buy</button>
        </div>
    {/if}
</div>