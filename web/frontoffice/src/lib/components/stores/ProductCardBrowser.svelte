<script lang="ts">
    import { onMount } from "svelte";
    import ProductCard from "$lib/components/stores/ProductCard.svelte";
    import {EVENT_KIND_AUCTION, EVENT_KIND_PRODUCT, getProducts} from "$sharedLib/services/nostr";
    import {filterTags, getFirstTagValue, getMerchantIDs} from "$sharedLib/nostr/utils";
    import {refreshStalls, onImgError} from "$lib/shopping";
    import Settings from "$sharedLib/components/icons/Settings.svelte";
    import ProductModal from "$lib/components/stores/ProductModal.svelte";
    import {fileConfiguration} from "$sharedLib/stores";
    import { browser } from '$app/environment'

    export let showOnlyProductsFromThisCommunity: boolean = false;
    export let maxProductsLoaded: number = 20;
    export let filter = null;
    export let showFixedPriceProducts = true;
    export let showAuctions = true;

    let productsLoaded = false;

    let numProductsLoaded: number = 0;
    let viewProductIdOnModal: string | null = null;
    let scrollPosition: number | null = null;

    let merchantIDs = [];

    if (browser && $fileConfiguration.backend_present) {
        getMerchantIDs()
            .then(merchantIDsFromAPI => {
                console.log('merchantIDsFromAPI', merchantIDsFromAPI);

                merchantIDsFromAPI.forEach(merchantIDFromAPI => {
                    if (merchantIDFromAPI && merchantIDFromAPI.public_key) {
                        merchantIDs.push(merchantIDFromAPI.public_key);
                    }
                });
            })
            .catch(error => console.log('Error loading merchant IDs from the community:', error));
    }

    /*
    interface CategoriesAssociativeArray {
        [key: string]: {
        amount: number,
        selected: boolean
        }
    }

    let categories: CategoriesAssociativeArray[] = [];
    categories['All'] = {
        amount: 0,
        selected: true
    };

    $: selectedCategories = Object.keys( Object.fromEntries( Object.entries(categories).filter(([category_id, category]) => {
        return category.selected;
    }) ) );
    */

    interface ProductsAssociativeArray {
        [key: string]: {}
    }
    let products: ProductsAssociativeArray[] = [];
    let filteredProducts = [];

    $: if (products) {
        numProductsLoaded = 0;

        filteredProducts = Object.fromEntries(Object.entries(products)
            .sort((a, b) => {
                return b[1].event.created_at - a[1].event.created_at;
            })
            .filter(([productId, product]) => {
                // Limit loaded products (0 means unlimited)
                if (maxProductsLoaded > 0 && numProductsLoaded >= maxProductsLoaded) {
                    return false;
                }

                // "Product of this community" filter
                if (showOnlyProductsFromThisCommunity && !merchantIDs.includes(product.event.pubkey)) {
                    return false;
                }

                // Text filter
                if (filter &&
                    !(
                        productId === filter ||
                        product.name?.toLowerCase().includes(filter.toLowerCase()) ||
                        product.description?.toLowerCase().includes(filter.toLowerCase()) ||
                        product.tags?.join(' ').toLowerCase().includes(filter.toLowerCase())
                    )
                ) {
                    return false;
                }

                // Product type filter
                if (!showAuctions && product.event.kind === EVENT_KIND_AUCTION) {
                    return false;
                }
                if (!showFixedPriceProducts && product.event.kind === EVENT_KIND_PRODUCT) {
                    return false;
                }

                numProductsLoaded++;
                return true;

                /*
                if (categories['All'].selected) {
                    return true;
                } else {
                    for (let i = 0; i < selectedCategories.length; i++) {
                        let categorySelected = selectedCategories[i];

                        if (product.tags && product.tags.includes(categorySelected)) {
                            return true;
                        }
                    }
                }
                */
            }));
    }

    onMount(async () => {
        refreshStalls();

        getProducts(null, null,
            (newProductInfo) => {
                if (!newProductInfo.image && (!newProductInfo.images || (newProductInfo.images && newProductInfo.images.length === 0 ) )) {
                    return;
                }

                // Calculate if auction is already ended
                if (newProductInfo.event.kind === EVENT_KIND_AUCTION) {
                    if (Math.floor(Date.now() / 1000) > (newProductInfo.start_date + newProductInfo.duration)) {     // Auction already ended
                        return;
                    }
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
                // EOSE: all products loaded
                if (browser) {
                    productsLoaded = true;
                }
            });
    });

    /*
    function toggleCategory(category) {
        if (category === 'All' && categories['All'].selected) {
            for (const cat in categories) {
                if (cat !== 'All') {
                    categories[cat].selected = false;
                }
            }
        } else {
            if (categories[category].selected) {
                categories['All'].selected = false;
            }
        }
    }
    */
</script>

<!--
<div class="p-2 py-2 pt-8 h-auto container grid align-center mx-auto">
    <div tabindex="0" class="lg:grid mt-3 mb-4 rounded-box collapse collapse-plus border border-gray-400/70 bg-base-100">
        <input type="checkbox" />
        <div class="collapse-title text-xl font-medium align-middle">
            <div class="size-8">
                <Settings />
            </div>

            {#if selectedCategories.length > 0 && !selectedCategories.includes('All')}
                <span class="ml-3">Filtering products from categories => </span>
                {#each selectedCategories as category}{category},&nbsp;{/each}
            {/if}
        </div>
        <div class="collapse-content columns-4">
            {#each Object.entries(categories) as [category, data]}
                <div class="label justify-normal mb-3">
                    <input type="checkbox" bind:checked={data.selected} on:change={() => toggleCategory(category)} class="checkbox checkbox-md mr-3" class:checkbox-success={data.selected} />
                    <span class="align-baseline text-xl">{category}</span> <span class="ml-2 text-sm">({data.amount})</span>
                </div>
            {/each}
        </div>
    </div>
</div>
-->

<div class="p-0 md:p-2 py-2 pt-4 md:pt-8 h-auto grid grid-cols-2 2xl:grid-cols-3 3xl:grid-cols-4 gap-4 lg:gap-12 2xl:gap-16 3xl:gap-20 align-center mx-auto" >
    {#each Object.entries(filteredProducts) as [_, product]}
        <ProductCard {product} {onImgError} isOnStall={false} bind:viewProductIdOnModal={viewProductIdOnModal} bind:scrollPosition={scrollPosition} />
    {/each}
</div>

<ProductModal bind:viewProductIdOnModal={viewProductIdOnModal} bind:scrollPosition={scrollPosition} />

{#if !productsLoaded}
    <div class="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-35 z-50">
        <div class="grid mx-auto w-fit p-28 items-center justify-center bg-white bg-opacity-80 rounded-2xl">
            <span class="mx-auto loading loading-bars w-48"></span>
            <p class="mx-auto mt-8 text-3xl">Loading products from the Nostrverse...</p>
        </div>
    </div>
{/if}