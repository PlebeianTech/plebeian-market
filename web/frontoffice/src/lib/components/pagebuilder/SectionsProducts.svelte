<script lang="ts">
    import {onMount} from "svelte";
    import {getItemsFromSection} from "$lib/pagebuilder";
    import {getProducts, EVENT_KIND_AUCTION, EVENT_KIND_PRODUCT} from "$sharedLib/services/nostr";
    import {getFirstTagValue} from "$sharedLib/nostr/utils";
    import ProductCard from "$lib/components/pagebuilder/ProductCard.svelte";

    export let pageId;
    export let sectionId;
    export let isSuperAdmin;

    let products: {[productId: string]: {}} = {};
    let productsLoaded = false;

    onMount(async () => {
        let productIDs = getItemsFromSection(pageId, sectionId, 'products');

        getProducts(null, productIDs,
            (newProductInfo) => {
                if (!newProductInfo.id) {
                    let productId = getFirstTagValue(newProductInfo.event.tags, 'd');
                    if (productId !== null) {
                        newProductInfo.id = productId;
                    } else {
                        return;
                    }
                }

                // Calculate if ended
                if (newProductInfo.event.kind === EVENT_KIND_AUCTION) {
                    let now = Math.floor(Date.now() / 1000);
                    let endsAt = newProductInfo.start_date + newProductInfo.duration;
                    newProductInfo.ended = now > endsAt;
                }

                let productId = newProductInfo.id;

                if (productId in products) {
                    if (products[productId].event.created_at < newProductInfo.event.created_at) {
                        products[productId] = newProductInfo;
                    }
                } else {
                    products[productId] = newProductInfo;
                }
            },
            () => {
                productsLoaded = true;
            });
    });
</script>

<main class="container mx-auto p-4">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-8 lg:gap-8 z-[300] mt-2 mb-2">
        {#if productsLoaded}
            {#each Object.entries(products) as [productId, product]}
                {#if product.event.kind === EVENT_KIND_PRODUCT || (product.event.kind === EVENT_KIND_AUCTION && (showExpiredAuctions || !showExpiredAuctions && product.ended === false) )}
                    <ProductCard {product} {isSuperAdmin} />
                {/if}
            {/each}
        {/if}
    </div>
</main>
