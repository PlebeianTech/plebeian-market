<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {ShoppingCart, stalls} from "$sharedLib/stores";
    import {deleteFromCart, onImgError} from "$lib/shopping";
    import Trash from "$sharedLib/components/icons/Trash.svelte";
    import Quantity from "./Quantity.svelte";

    export let compact = false;

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

            for (const [_, stall] of $ShoppingCart.products) {
                stalls++;
                for (const [_, product] of stall) {
                    numProducts++;
                    totalQuantity = totalQuantity + product.orderQuantity;
                }
            }

            $ShoppingCart.summary = {
                numProducts: numProducts,
                totalQuantity: totalQuantity,
                stalls: stalls
            };
        }
    }
</script>

<div class="md:grid justify-center">
{#if $ShoppingCart.summary.numProducts && $stalls && $stalls.stalls}
    <!-- Desktop -->
    <table class="hidden md:block table table-auto w-full {compact ? 'table-md' : 'border rounded border-gray-400'}" >
        <thead>
            <tr class="text-center">
                <th>Name</th>
                {#if !compact}
                    <th>Description</th>
                {/if}
                <th>Price</th>
                <th>Quantity</th>
                <th>Image</th>
                <th>Total</th>
                <th></th>
            </tr>
        </thead>

        <tbody>
        {#each [...$ShoppingCart.products] as [stallId, products]}
            {#if $stalls.stalls[stallId]}
                <tr>
                    <td colspan="{compact ? 6 : 7}" class="bg-gray-300 dark:bg-gray-700">
                        <p class="ml-3">
                            <a href="/p/{$stalls.stalls[stallId].merchantPubkey}/stall/{$stalls.stalls[stallId].id}">
                                {#if $stalls !== null && $stalls.stalls[stallId]}
                                    Stall: {$stalls.stalls[stallId].name ?? ''}
                                {:else}
                                    Stall id: {stallId}
                                {/if}
                            </a>
                        </p>
                    </td>
                </tr>

                {#each [...products] as [_, product]}
                    <tr>
                        <th>{#if product.name}<a href="/product/{product.id}">{product.name}</a>{/if}</th>
                        {#if !compact}
                            <td>{#if product.description}{product.description.substring(0,80)}{#if product.description.length > 80}...{/if}{/if}</td>
                        {/if}
                        <td class="text-center">{#if product.price}{product.price} {#if product.currency}{product.currency}{/if}{/if}</td>
                        <td>
                            <Quantity bind:quantity={product.orderQuantity} maxStock={product.quantity} {compact} />
                        </td>
                        <td>
                            <div class="card shadow-xl { compact ? 'w-16' : 'w-32'}">
                                <img class:rounded-xl={!compact} src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} />
                            </div>
                        </td>
                        <td class="text-center">{(product.orderQuantity ?? 0) * product.price} {#if product.currency}{product.currency}{/if}</td>
                        <th class="cursor-pointer mr-4" on:click={() => deleteFromCart(stallId, product.id)}>
                            <div class="w-5 h-5 tooltip tooltip-error" data-tip="{ compact ? 'Remove product' : 'Remove product from shopping cart'}"><Trash /></div>
                        </th>
                    </tr>
                {/each}
            {:else}
                <tr>Loading stall information...</tr>
            {/if}
        {/each}
        </tbody>
    </table>

    <!-- Mobile -->
    <table class="table table-auto w-full md:hidden text-left {compact ? 'table-sm' : 'border rounded border-gray-400'}">
        <thead>
            <tr class="text-center">
                <th class="text-left pl-1 pr-0">Name</th>
                <th class="px-0">Price</th>
                <th class="px-1">Quantity</th>
                <th class="px-0">Total</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {#each [...$ShoppingCart.products] as [stallId, products]}
                {#if $stalls.stalls[stallId]}
                    <tr class="bg-gray-300 dark:bg-gray-700">
                        <td colspan="5">
                            <p class:mx-3={!compact}>
                                <a href="/p/{$stalls.stalls[stallId].merchantPubkey}/stall/{$stalls.stalls[stallId].id}">
                                    {#if $stalls !== null && $stalls.stalls[stallId]}
                                        Stall: {$stalls.stalls[stallId].name ?? ''}
                                    {:else}
                                        Stall id: {stallId}
                                    {/if}
                                </a>
                            </p>
                        </td>
                    </tr>

                    {#each [...products] as [_, product]}
                        <tr class="text-xs text-center">
                            <th class="text-left text-xs pl-1 pr-0">{#if product.name}<a href="/product/{product.id}">{product.name}</a>{/if}</th>
                            <td class="px-0">{#if product.price}{product.price} {#if product.currency}{product.currency}{/if}{/if}</td>
                            <td class="px-1">
                                <Quantity bind:quantity={product.orderQuantity} maxStock={product.quantity} {compact} />
                            </td>
                            <td class="px-0">{(product.orderQuantity ?? 0) * product.price} {#if product.currency}{product.currency}{/if}</td>
                            <td class="pl-1 pr-1" on:click={() => deleteFromCart(stallId, product.id)}>
                                <div class="w-5 h-5"><Trash /></div>
                            </td>
                        </tr>
                    {/each}
                {:else}
                    <tr>Loading stall information...</tr>
                {/if}
            {/each}
        </tbody>
    </table>

    {#if compact}
        <div class="mt-6 card-actions justify-center">
            <a class="btn btn-primary btn-block" href="/cart">See cart details</a>
        </div>
    {:else}
        <div class="mt-6 card-actions justify-center">
            <a class="btn btn-info mr-1" href="/stalls">Continue shopping</a>
            <a class="btn btn-success" href="/checkout">Checkout</a>
        </div>
    {/if}
{:else}
        <div class="p-6 text-lg" class:w-64={compact}>
            <p>The shopping cart is empty.</p>
            <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stalls</a> and buy some products.</p>
            <p class="mt-4">You can check the <a class="text-blue-500" href="/orders">Orders</a> screen to check the status of your orders.</p>
        </div>

        {#if !compact}
            <div class="mt-6 card-actions justify-center" class:justify-end={$ShoppingCart.summary.numProducts}>
                <a class="btn btn-primary" href="/stalls">Continue shopping</a>
            </div>
        {/if}
{/if}
</div>
