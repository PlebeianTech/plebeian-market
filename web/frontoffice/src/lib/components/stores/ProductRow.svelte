<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Quantity from "$lib/components/stores/Quantity.svelte";
    import {addToCart} from "$lib/shopping";
    import {EVENT_KIND_AUCTION} from "$lib/services/nostr";
    import {goto} from "$app/navigation";

    export let product: string;
    export let onImgError = () => {};
    export let orderQuantity = 1;
</script>

<tr>
    <td>{#if product.name}<a class="hover:underline" href="/product/{product.id}">{product.name}</a>{/if}</td>
    <td>{#if product.description}{product.description}{/if}</td>
    <td>
        {#if product.event.kind === EVENT_KIND_AUCTION}
            <div class="badge badge-info gap-2">auction</div>
        {:else}
            <div class="badge badge-success gap-2">fixed price</div>
        {/if}
    </td>
    <td class="text-center">
        {#if product.event.kind !== EVENT_KIND_AUCTION}
            {product.quantity ?? 0}
        {/if}
    </td>
    <td class="text-center">
        {#if product.event.kind !== EVENT_KIND_AUCTION}
            {#if product.price}{product.price} {#if product.currency} {product.currency}{/if}{/if}
        {/if}
    </td>
    <td>
        <div class="card bg-base-100 shadow-xl w-full lg:w-32">
            <figure><a href="/product/{product.id}"><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></a></figure>
        </div>
    </td>

    {#if product.event.kind !== EVENT_KIND_AUCTION}
        <td class="{!product.quantity ? 'tooltip tooltip-warning' : ''}" data-tip="Out of stock">
            <Quantity bind:quantity={orderQuantity} maxStock={product.quantity} />
            <button class="btn btn-primary" class:btn-disabled={!product.quantity} on:click|preventDefault={(event) => addToCart(product, orderQuantity)}>
                Add to cart
            </button>
        </td>
    {:else}
        <td>
            <button class="btn btn-primary" on:click|preventDefault={() => goto('/product/' + product.id)}>
                View
            </button>
        </td>
    {/if}
</tr>
