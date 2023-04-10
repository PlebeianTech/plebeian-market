<script lang="ts">
    import Plus from "$lib/components/icons/Plus.svelte";
    import Minus from "$lib/components/icons/Minus.svelte";
    import {Error} from "$lib/stores";

    export let quantity;
    export let maxStock;
    export let compact = false;

    export function onQtyChange(plus = false) {
        if (quantity === 1 && !plus) {
            return;
        }

        plus ? quantity++ : quantity--;

        if (quantity > maxStock) {
            Error.set('There are just ' + maxStock + ' products in stock. You cannot order ' + quantity);
            quantity--;
        }
    }
</script>

<div class="flex items-center mb-2 " class:space-x-1={!compact}>
    <button type="button" on:click|preventDefault={() => onQtyChange()} class="p-1 text-gray-500 rounded-full hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700">
        <Minus />
    </button>
    <input bind:value={quantity} type="number" class="block w-14 text-center rounded-lg py-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
    <button type="button" on:click|preventDefault={() => onQtyChange(true)}  class="p-1 text-gray-500 rounded-full hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700">
        <Plus />
    </button>
</div>
