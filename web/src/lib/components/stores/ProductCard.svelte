<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Quantity from "./Quantity.svelte";
    import {addToCart} from "$lib/shopping";

    export let product: string;
    export let onImgError = () => {};
    export let orderQuantity = 1;
</script>

<div class="card w-96 bg-base-100 shadow-xl mx-auto">
    <figure><img src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
    <div class="card-body items-center text-center">
        <h2 class="card-title">
            {#if product.name}{product.name}{/if}
            <!-- <div class="badge badge-secondary">NEW</div> -->
        </h2>
        <div class="mb-4">{#if product.description}{product.description}{/if}</div>
        <!--
        <div class="card-actions justify-end mb-4">
            <div class="badge badge-outline">Fashion</div>
            <div class="badge badge-outline">Products</div>
        </div> -->
        <div class="columns-2">
            <div>
                Stock: {product.quantity ?? 0}
            </div>
            <div>{#if product.price}{product.price} {#if product.currency} {product.currency}{/if}{/if}</div>
        </div>
        <div class="mt-10 justify-end {!product.quantity ? 'tooltip tooltip-warning' : ''}" data-tip="Out of stock">
            <Quantity bind:quantity={orderQuantity} maxStock={product.quantity} />
            <button class="btn btn-primary mt-4" class:btn-disabled={!product.quantity} on:click|preventDefault={(event) => addToCart(product, orderQuantity)}>
                Add to cart
            </button>
        </div>
    </div>
</div>
