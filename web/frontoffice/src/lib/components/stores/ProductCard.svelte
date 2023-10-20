<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Quantity from "./Quantity.svelte";
    import {addToCart} from "$lib/shopping";
    import {stalls} from "$sharedLib/stores";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import { goto } from "$app/navigation";
    import {EVENT_KIND_AUCTION} from "$sharedLib/services/nostr";
    import AuctionInfo from "$lib/components/stores/AuctionInfo.svelte";
    import { Image } from 'svelte-lazy-loader';

    export let product;
    export let onImgError = () => {};
    export let isOnStall: boolean;
    export let orderQuantity = 1;
    export let viewProductIdOnModal: string | null = null;
    export let scrollPosition: number | null = null;

    function openProduct() {
        scrollPosition = document.documentElement.scrollTop; viewProductIdOnModal = product.id;
    }
</script>

<div class="card w-full md:w-96 bg-base-200 dark:bg-base-300 shadow-xl mx-auto mb-16 md:4">
    <figure>
        <a class="cursor-pointer" href="/product/{product.id}" on:click|preventDefault={openProduct}>
            {#key `${product.id}-${product.images ? product.images[0] : product.image ?? productImageFallback}`}
                <Image
                    loading="lazy"
                    placeholder="{productImageFallback}"
                    src="{product.images ? product.images[0] : product.image ?? productImageFallback}" />
            {/key}
        </a>
    </figure>
    <div class="card-body items-center text-center">
        {#if product.event.kind === EVENT_KIND_AUCTION}
            <div class="badge badge-info gap-2">auction</div>
        {:else}
            <div class="badge badge-success gap-2 mb-2">fixed price</div>
        {/if}

        <h2 class="card-title">
            {#if product.name}<a class="cursor-pointer hover:underline" href="/product/{product.id}" on:click|preventDefault={openProduct}>{product.name}</a>{/if}
        </h2>

        {#if !isOnStall && $stalls !== null && $stalls.stalls[product.stall_id]}
            <div class="alert bg-purple-500/30 hover:bg-purple-500/60 tooltip tooltip-left tooltip-primary cursor-pointer" data-tip="Visit stall" on:click|preventDefault={() => goto('/p/'+product.event.pubkey+'/stall/'+product.stall_id)}>
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

        {#if product.event.kind === EVENT_KIND_AUCTION}
            <AuctionInfo {product} />
        {:else}
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
        {/if}
    </div>
</div>
