<script lang="ts">
    import {onMount} from "svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {EVENT_KIND_AUCTION, EVENT_KIND_PRODUCT, getProducts} from "$sharedLib/services/nostr";
    import {onImgError, refreshStalls} from "$lib/shopping";
    import {afterNavigate, goto} from "$app/navigation";
    import {stalls} from "$sharedLib/stores";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import Quantity from "$lib/components/stores/Quantity.svelte";
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {addToCart} from "$lib/shopping";
    import {filterTags} from "$sharedLib/nostr/utils";
    import BidWidget from "$lib/components/stores/BidWidget.svelte";

    export let product_id = null;
    export let in_popup = false;

    let product = null;
    let orderQuantity = 1;
    let activeImage = null;

    function loadProduct() {
        product = null;

        if (product_id) {
            getProducts(null, [product_id],
                (productEvent) => {
                    if (!product || (product && productEvent.created_at > product.event.created_at)) {
                        product = JSON.parse(productEvent.content);
                        product.event = productEvent;

                        let categoryTags = filterTags(productEvent.tags, 't');
                        if (categoryTags.length > 0) {
                            categoryTags.forEach((category) => {
                                let tag = category[1].trim().toLowerCase();

                                // vitamin the product with categories
                                if (product.tags) {
                                    product.tags.push(tag);
                                } else {
                                    product.tags = [tag];
                                }
                            });
                        }
                    }
                });
        }
    }

    afterNavigate(() => {
        loadProduct();
    });

    onMount(async () => {
        loadProduct();
        refreshStalls();
    });
</script>

<svelte:head>
    <title>Product</title>
</svelte:head>

{#if product}
    {#if in_popup}
        <Titleh1 titleClass="p-4 mt-3 md:-mt-2 mb-3 md:mb-5 text-center text-3xl lg:text-3xl">{product.name}</Titleh1>
    {:else}
        <Titleh1>{product.name}</Titleh1>
    {/if}

    <div class="grid justify-center items-center mb-10 {in_popup ? 'lg:mx-10' : 'md:mb-20 lg:mx-20'} ">
        <div class="flex flex-col w-full md:flex-row">

            <!-- Left (images) -->
            <div class="md:flex w-full md:max-w-[50%]">
                <!-- Desktop image chooser -->
                {#if product.images && product.images.length > 1}
                    <div class="hidden md:block md:w-1/12 container mx-auto">
                        <div class="flex flex-wrap md:-m-2">
                            {#if product.images}
                                {#each product.images as image, i}
                                    <div class="p-1 md:p-2">
                                        <img class="block h-full w-full rounded-lg cursor-pointer {activeImage===image || activeImage===null && i===0 ? 'border-2 border-rose-500' : ''}" on:mouseenter={() => activeImage = image}
                                             src="{image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} />
                                    </div>
                                {/each}
                            {/if}
                        </div>
                    </div>
                {/if}

                <div class="w-full align-top mb-5 md:mb-0 {product.images && product.images.length > 1 ? 'md:w-8/12' : 'md:w-12/12' }">
                    <img class="rounded-lg min-w-full" src="{activeImage ? activeImage : product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} />
                </div>

                <!-- Mobile image chooser -->
                {#if product.images && product.images.length > 1}
                    <div class="md:hidden w-full container mx-auto">
                        <div class="flex flex-wrap">
                            {#if product.images}
                                {#each product.images as image, i}
                                    <div class="flex w-1/4 p-1">
                                        <img class="block h-full w-full rounded-lg cursor-pointer {activeImage===image || activeImage===null && i===0 ? 'border-2 border-rose-500' : ''}" on:mouseenter={() => activeImage = image}
                                             src="{image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} />
                                    </div>
                                {/each}
                            {/if}
                        </div>
                    </div>
                {/if}
            </div>

            <div class="divider md:divider-horizontal my-2 md:my-4"></div>

            <div class="w-full h-fit md:p-8 md:pt-0 place-items-center place-content-center text-center text-2xl">
                <div class="mb-8 text-xl">{#if product.description}{product.description}{/if}</div>

                {#if product.event.kind === EVENT_KIND_AUCTION}
                    <div class="mb-8">
                        <BidWidget {product} />
                    </div>
                {/if}

                {#if product.tags}
                    <div class="card-actions justify-center mb-12">
                        {#each product.tags as tag}
                            <div class="badge badge-outline badge-lg text-lg p-4">{tag}</div>
                        {/each}
                    </div>
                {/if}

                {#if $stalls !== null && $stalls.stalls[product.stall_id]}
                    <div class="md:max-w-[70%] alert bg-purple-500/30 hover:bg-purple-500/60 tooltip tooltip-left tooltip-primary cursor-pointer text-lg" data-tip="Visit stall" on:click|preventDefault={() => goto('/p/'+product.event.pubkey+'/stall/'+product.stall_id)}>
                        <div class="float-left h-6 w-6 mr-1 align-middle stroke-current flex-shrink-0">
                            <Store />
                        </div>
                        {$stalls.stalls[product.stall_id].name}
                    </div>
                {/if}

                {#if product.event.kind === EVENT_KIND_PRODUCT}
                    <div class="columns-2 my-12">
                        <div>
                            {#if product.quantity === null}
                                Stock: Unlimited
                            {:else}
                                Stock: {product.quantity}
                            {/if}
                        </div>
                        <div>{#if product.price}{product.price} {#if product.currency} {product.currency}{/if}{/if}</div>
                    </div>

                    {#if product.quantity === null || product.quantity > 0}
                        <div class="block mb-6 text-xl">
                            <div class="flex justify-center">
                                <Quantity bind:quantity={orderQuantity} maxStock={product.quantity} />
                            </div>
                            <button class="btn btn-primary mt-2" class:btn-disabled={product.quantity === 0} on:click|preventDefault={(event) => addToCart(product, orderQuantity)}>
                                Add to cart
                            </button>
                        </div>
                    {:else}
                        <button class="btn btn-warning btn-lg no-animation">Out of stock</button>
                    {/if}
                {/if}
            </div>
        </div>
    </div>
{/if}
