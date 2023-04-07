<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {ShoppingCart} from "../../stores";
    import {deleteFromCart, onImgError} from "$lib/shopping";
    import {browser} from "$app/environment";
    import Trash from "../icons/Trash.svelte";

    export let compact: boolean;

    $: {
        // When you are viewing the full-featured-cart, you'll run this code twice: one for the compact cart
        // that is always visible at the NavBar, and the other one for the Cart page.
        //
        // It seems one of the runs interferes with the other one, and they enter a loop. Probably have
        // something to do with the reactivity: you're updating a store when there are changes in the store,
        // and then you're making calls to the same store at the same time...
        //
        // This "if" makes that this runs just once when viewing the full-featured shopping cart.

        if (compact) {
            let numProducts = 0;
            let totalQuantity = 0;
            let totalAmount = 0;
            let currency = '';

            for (const [stallId, stall] of $ShoppingCart.products) {
                for (const [productId, product] of stall) {
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
        <a class="btn btn-primary" href="/stalls">Continue shopping</a>
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
        {#each [...$ShoppingCart.products] as [stallId, products]}
            <tr>
                <td colspan="{compact ? 5 : 7}" class="bg-gray-700"><p class="ml-3">Stall: {stallId}</p></td>
            </tr>

            {#each [...products] as [productId, product]}
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
                    <td class="hover cursor-pointer" on:click={() => deleteFromCart(stallId, product.id)}>
                        <Trash />
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
            <a class="btn btn-primary" href="/stalls">Continue shopping</a>
            <a class="btn btn-accent" href="/stalls">Checkout</a>
        </div>
    {/if}
{:else}
    <div class="p-6 text-lg" class:w-64={compact}>
        <p>The shopping cart is empty.</p>
        <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stores</a> and buy some products.</p>
    </div>
{/if}
