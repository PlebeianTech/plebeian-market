<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {ShoppingCart, stalls} from "../../stores";
    import {deleteFromCart, onImgError} from "$lib/shopping";
    import {browser} from "$app/environment";
    import Trash from "../../../../src/lib/components/icons/Trash.svelte";
    import Quantity from "./Quantity.svelte";

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
            let stalls = 0;

            for (const [stallId, stall] of $ShoppingCart.products) {
                stalls++;
                for (const [productId, product] of stall) {
                    numProducts++;
                    totalQuantity = totalQuantity + product.orderQuantity;
                }
            }

            $ShoppingCart.summary = {
                numProducts: numProducts,
                totalQuantity: totalQuantity,
                stalls: stalls
            };

            //if (browser) {
            //    localStorage.setItem('shoppingCart', JSON.stringify($ShoppingCart));
            //}
        }
    }
</script>

{#if $ShoppingCart.summary.numProducts}
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
                <td colspan="{compact ? 5 : 7}" class="bg-gray-700">
                    <p class="ml-3">
                        {#if $stalls !== null && $stalls.stalls[stallId]}
                            Stall: {$stalls.stalls[stallId].name ?? ''}
                        {:else}
                            Stall id: {stallId}
                        {/if}
                    </p>
                </td>
            </tr>

            {#each [...products] as [productId, product]}
                <tr class="text-center">
                    <td>{#if product.name}{product.name}{/if}</td>
                    {#if !compact}
                        <td>{#if product.description}{product.description.substring(0,80)}{#if product.description.length > 80}...{/if}{/if}</td>
                    {/if}
                    <td>{#if product.price}{product.price} {#if product.currency}{product.currency}{/if}{/if}</td>
                    <td>
                        <Quantity bind:quantity={product.orderQuantity} maxStock={product.quantity} {compact} />
                    </td>
                    {#if !compact}
                        <td>
                            <div class="card bg-base-100 shadow-xl w-full lg:w-32">
                                <figure><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
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
        <div class="card-actions justify-end">
            <a class="btn btn-primary btn-block" href="/cart">See cart details</a>
        </div>
    {:else}
        <div class="card-actions justify-end">
            <a class="btn btn-primary" href="/stalls">Continue shopping</a>
            <a class="btn btn-accent" href="/checkout">Checkout</a>
        </div>
    {/if}
{:else}
    <div class="p-6 text-lg" class:w-64={compact}>
        <p>The shopping cart is empty.</p>
        <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stalls</a> and buy some products.</p>
    </div>

    {#if !compact}
        <div class="card-actions justify-center" class:justify-end={$ShoppingCart.summary.numProducts}>
            <a class="btn btn-primary" href="/stalls">Continue shopping</a>
        </div>
    {/if}
{/if}
