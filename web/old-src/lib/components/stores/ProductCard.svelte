<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Quantity from "./Quantity.svelte";
    import {addToCart} from "$lib/shopping";
    import {stalls} from "$lib/stores";

    export let product: string;
    export let onImgError = () => {};
    export let orderQuantity = 1;
</script>

<div class="card w-96 bg-base-100 shadow-xl mx-auto">
    <figure><img src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
    <div class="card-body items-center text-center">
        <h2 class="card-title">
            {#if product.name}{product.name}{/if}
        </h2>
        {#if $stalls !== null && $stalls.stalls[product.stall_id]}
            <a class="badge badge-secondary tooltip tooltip-left tooltip-primary" data-tip="Visit stall" href="/p/{product.merchantPubkey}/stall/{product.stall_id}">{$stalls.stalls[product.stall_id].name}</a>
        {/if}
        <div class="mb-4">{#if product.description}{product.description}{/if}</div>
        {#if product.tags}
            <div class="card-actions justify-end mb-4">
                {#each product.tags as tag}
                    <div class="badge badge-outline">{tag}</div>
                {/each}
            </div>
        {/if}
        <div class="columns-2">
            <div>
                Stock: {product.quantity ?? 0}
            </div>
            <div>{#if product.price}{product.price} {#if product.currency} {product.currency}{/if}{/if}</div>
        </div>
        <div class="mt-5 justify-end {!product.quantity ? 'tooltip tooltip-warning' : ''}" data-tip="Out of stock">
            <Quantity bind:quantity={orderQuantity} maxStock={product.quantity} />
            <button class="btn btn-primary mt-4" class:btn-disabled={!product.quantity} on:click|preventDefault={(event) => addToCart(product, orderQuantity)}>
                Add to cart
            </button>
        </div>
    </div>
</div>
