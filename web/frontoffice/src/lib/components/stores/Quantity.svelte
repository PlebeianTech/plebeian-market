<script lang="ts">
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import Minus from "$sharedLib/components/icons/Minus.svelte";
    import {Error} from "$sharedLib/stores";
    import {saveShoppingCartProductsToLocalStorage} from "$lib/shopping";

    export let quantity;
    export let maxStock;
    export let compact = false;

    export function onQtyChange(plus = false) {
        if (quantity === 1 && !plus) {
            return;
        }

        plus ? quantity++ : quantity--;

        if (maxStock !== null && quantity > maxStock) {
            Error.set('There are just ' + maxStock + ' products in stock. You cannot order ' + quantity);
            quantity--;
        }

        saveShoppingCartProductsToLocalStorage();
    }
</script>

<div class="flex items-center mb-2" class:space-x-1={!compact}>
    <button type="button"
            on:click|preventDefault={() => onQtyChange()}
            class="p-1 text-gray-500 rounded-full hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600"
            class:w-6={compact} class:w-8={!compact}>
        <Minus />
    </button>
    <input bind:value={quantity}
           type="number"
           class="block w-14 text-center rounded-lg py-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
           class:w-6={compact} class:w-9={!compact}>
    <button type="button"
            on:click|preventDefault={() => onQtyChange(true)}
            class="p-1 text-gray-500 rounded-full hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600"
            class:w-6={compact} class:w-8={!compact}>
        <Plus />
    </button>
</div>
