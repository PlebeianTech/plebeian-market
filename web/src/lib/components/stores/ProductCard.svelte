<script lang="ts">
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    export let product: string;
    export let onImgError = (image) => {
        image.onerror = "";
        image.src = profilePicturePlaceHolder;
    }
</script>

<div class="card w-96 bg-base-100 shadow-xl">
    <figure><img src="{product.image ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} /></figure>
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
                Qty: {product.quantity ?? 0}
            </div>
            <div>{#if product.price}{product.price} {#if product.currency} {product.currency}{/if}{/if}</div>
        </div>
        <div class="card-actions justify-end {!product.quantity ? 'tooltip tooltip-warning' : ''}" data-tip="Out of stock">
            <button class="btn btn-primary mt-4" class:btn-disabled={!product.quantity} on:click|preventDefault={() => console.log('Added to cart')}>Add to cart</button>
        </div>
    </div>
</div>
