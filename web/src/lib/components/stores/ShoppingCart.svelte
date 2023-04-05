<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {ShoppingCart} from "../../stores";
    import {deleteFromCart, onImgError} from "../../services/shopping";
    import {browser} from "$app/environment";

    export let compact: boolean;

    $: {
        // Run only on the compact shopping cart when also viewing full-featured shopping cart
        if (compact) {
            let numProducts = 0;
            let totalQuantity = 0;
            let totalAmount = 0;
            let currency = '';

            for (const [stall_id, stall] of $ShoppingCart.products) {
                for (const [product_id, product] of stall) {
                    numProducts++;
                    totalQuantity = totalQuantity + product.orderQuantity;
                    totalAmount = totalAmount + (product.orderQuantity * product.price);
                    currency = product.currency;
                }
            }

            $ShoppingCart.summary = {
                numProducts: numProducts,
                totalQuantity: totalQuantity,
                totalAmount: totalAmount,
                currency: currency
            };

            //if (browser) {
            //    localStorage.setItem('shoppingCart', JSON.stringify($ShoppingCart));
            //}
        }
    }
</script>

{#if !compact}
    <div class="card-actions justify-end">
        <a class="btn btn-primary" href="/store_browser">Continue shopping</a>
    </div>
{/if}

{#if $ShoppingCart.summary.numProducts > 0}
    <table class="table table-auto w-full place-content-center" class:table-compact={compact}>
        <thead>
        <tr class="text-center">
            <th>Name</th>
            {#if !compact}
                <th>Description</th>
            {/if}
            <th>Price</th>
            <th>Quantity</th>
            {#if !compact}
                <th>Image</th>
            {/if}
            <th>Total</th>
            <th></th>
        </tr>
        </thead>

        <tbody>
        {#each [...$ShoppingCart.products] as [stall_id, products]}
            <tr>
                <td colspan="{compact ? 5 : 7}" class="bg-gray-700"><p class="ml-3">Stall: {stall_id}</p></td>
            </tr>

            {#each [...products] as [product_id, product]}
                <tr class="text-center">
                    <td>{#if product.name}{product.name}{/if}</td>
                    {#if !compact}
                        <td>{#if product.description}{product.description}{/if}</td>
                    {/if}
                    <td>{#if product.price}{product.price} {#if product.currency}{product.currency}{/if}{/if}</td>
                    <td>
                        <div class="flex items-center" class:space-x-1={compact} class:space-x-3={!compact}>
                            <button class="inline-flex items-center p-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                                <span class="sr-only">Quantity button</span>
                                <svg class:w-3={compact} class:h-3={compact} class:w-4={!compact} class:h-4={!compact} aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
                            </button>
                            <div>
                                <input type="number" id="first_product" class="bg-gray-50 w-10 border border-gray-300 text-gray-900 text-sm text-center rounded-lg focus:ring-blue-500 focus:border-blue-500 block px-2.5 py-1 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="1" value="{product.orderQuantity ?? 0}" required>
                            </div>
                            <button class="inline-flex items-center p-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                                <span class="sr-only">Quantity button</span>
                                <svg class:w-3={compact} class:h-3={compact} class:w-4={!compact} class:h-4={!compact} aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"></path></svg>
                            </button>
                        </div>
                    </td>
                    {#if !compact}
                        <td>
                            <div class="card bg-base-100 shadow-xl w-full lg:w-32">
                                <figure><img class="rounded-xl" src="{product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
                            </div>
                        </td>
                    {/if}
                    <td>{(product.orderQuantity ?? 0) * product.price} {#if product.currency}{product.currency}{/if}</td>
                    <td class="hover cursor-pointer" on:click={() => deleteFromCart(stall_id, product.id)}>
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                        </svg>
                    </td>
                </tr>
            {/each}
        {/each}
        </tbody>
    </table>

    {#if compact}
        <span class="text-xl text-white align-right text-right my-2">Subtotal: {$ShoppingCart.summary.totalAmount} {$ShoppingCart.summary.currency}</span>

        <div class="card-actions justify-end">
            <a class="btn btn-primary btn-block" href="/cart">See cart details</a>
        </div>
    {/if}

    {#if !compact}
        <!-- <span class="font-bold text-lg">{$ShoppingCart.summary.numProducts} different Items</span> -->

        <div class="card-actions justify-end">
            <a class="btn btn-primary" href="/store_browser">Continue shopping</a>
            <a class="btn btn-accent" href="/store_browser">Checkout</a>
        </div>
    {/if}
{:else}
    <div class="p-6 text-lg" class:w-64={compact}>
        <p>The shopping cart is empty.</p>
        <p class="mt-4">You can <a class="text-blue-500" href="/store_browser">browse stores</a> and buy some products.</p>
    </div>
{/if}
