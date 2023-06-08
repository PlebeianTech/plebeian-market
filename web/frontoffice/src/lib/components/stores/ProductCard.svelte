<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Quantity from "./Quantity.svelte";
    import {addToCart} from "$lib/shopping";
    import {stalls} from "$lib/stores";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import { goto } from "$app/navigation";

    export let product: string;
    export let onImgError = () => {};
    export let isOnStall: boolean;
    export let orderQuantity = 1;
</script>

<div class="card w-full md:w-96 bg-base-200 dark:bg-base-300 shadow-xl mx-auto mb-16 md:4">
    <figure><a href="/product/{product.id}"><img src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></a></figure>
    <div class="card-body items-center text-center">
        <h2 class="card-title">
            {#if product.name}<a class="hover:underline" href="/product/{product.id}">{product.name}</a>{/if}
        </h2>

        {#if !isOnStall && $stalls !== null && $stalls.stalls[product.stall_id]}
            <div class="alert bg-purple-500/30 hover:bg-purple-500/60 tooltip tooltip-left tooltip-primary cursor-pointer" data-tip="Visit stall" on:click|preventDefault={() => goto('/p/'+product.merchantPubkey+'/stall/'+product.stall_id)}>
                    <span class="text-sm">
                        <div class="float-left mr-2 align-middle stroke-current flex-shrink-0 h-6 w-6">
                            <Store />
                        </div>
                        {$stalls.stalls[product.stall_id].name}
                    </span>
            </div>
        {/if}

        <div class="mb-4">{#if product.description}{product.description}{/if}</div>
        {#if product.tags}
            <div class="card-actions justify-center mb-4">
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
        <div class="mt-3 justify-end {!product.quantity ? 'tooltip tooltip-warning' : ''}" data-tip="Out of stock">
            <Quantity bind:quantity={orderQuantity} maxStock={product.quantity} />
            <button class="btn btn-primary mt-4" class:btn-disabled={!product.quantity} on:click|preventDefault={(event) => addToCart(product, orderQuantity)}>
                Add to cart
            </button>
        </div>
    </div>
</div>
