<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Quantity from "$lib/components/stores/Quantity.svelte";

    export let product: string;
    export let addToCart = () => {};
    export let onImgError = () => {};
    export let onQtyChangeClick = () => {};
</script>

<tr>
    <td>{#if product.name}{product.name}{/if}</td>
    <td>{#if product.description}{product.description}{/if}</td>
    <td class="text-center">{product.quantity ?? 0}</td>
    <td class="text-center">{#if product.price}{product.price} {#if product.currency} {product.currency}{/if}{/if}</td>
    <td>
        <div class="card bg-base-100 shadow-xl w-full lg:w-32">
            <figure><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
        </div>
    </td>
    <td class="{!product.quantity ? 'tooltip tooltip-warning' : ''}" data-tip="Out of stock">
        <Quantity {onQtyChangeClick}></Quantity>
        <button class="btn btn-primary" class:btn-disabled={!product.quantity} on:click|preventDefault={(event) => addToCart(product, event)}>
            Add to cart
        </button>
    </td>
</tr>
