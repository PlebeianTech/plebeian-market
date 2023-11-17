<script lang="ts">
    import { onMount } from "svelte";
    import ProductCard from "$lib/components/stores/ProductCard.svelte";
    import {EVENT_KIND_AUCTION, getProducts} from "$sharedLib/services/nostr";
    import {filterTags, getFirstTagValue, getMerchantIDs} from "$sharedLib/nostr/utils";
    import {refreshStalls, onImgError} from "$lib/shopping";
    import {getConfigurationFromFile} from "$sharedLib/utils";
    import Settings from "$sharedLib/components/icons/Settings.svelte";
    import ProductModal from "$lib/components/stores/ProductModal.svelte";

    export let whiteListedStalls: string | null = null;
    export let showOnlyPMProducts: boolean = false;
    export let maxProductsLoaded: number = 20;

    let productsLoaded: number = 0;
    let viewProductIdOnModal: string | null = null;
    let scrollPosition: number | null = null;

    let merchantIDs = [];

    $: backend_present = true;

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

    interface ProductsAssociativeArray {
        [key: string]: {}
    }
    let products: ProductsAssociativeArray[] = [];   // : {[productId: string]: {}} = {};

    $: filteredProducts = Object.fromEntries( Object.entries(products).filter(([productId, product]) => {
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
    }));

    onMount(async () => {
        refreshStalls();

        let config = await getConfigurationFromFile();

        if (config && config.admin_pubkeys.length > 0) {
            backend_present = config.backend_present ?? true;

            if (showOnlyPMProducts && backend_present) {
                const merchantIDsFromAPI = await getMerchantIDs();

                merchantIDsFromAPI.forEach(merchantIDFromAPI => {
                    if (merchantIDFromAPI) {
                        merchantIDs.push(merchantIDFromAPI);
                    }
                });
            }

            // admin pubkey specified, so let's wait
            // to give some time for the homepage setup
            // to get here from Nostr relays...
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        getProducts(null, null,
            (newProductInfo) => {
                if (!newProductInfo.image && (!newProductInfo.images || (newProductInfo.images && newProductInfo.images.length === 0 ) )) {
                    return;
                }

                // Calculate if auction is already ended
                if (newProductInfo.event.kind === EVENT_KIND_AUCTION) {
                    let now = Math.floor(Date.now() / 1000);
                    let endsAt = newProductInfo.start_date + newProductInfo.duration;

                    if (now > endsAt) {
                        // Auction already ended
                        return;
                    }
                }

                if (!newProductInfo.id) {
                    let productId = getFirstTagValue(newProductInfo.event.tags, 'd');
                    if (productId !== null) {
                        newProductInfo.id = productId;
                    } else {
                        return;
                    }
                }

                if (showOnlyPMProducts && backend_present && !merchantIDs.includes(newProductInfo.event.pubkey)) {
                    return;
                }

                filterTags(newProductInfo.event.tags, 't').forEach((category) => {
                    let tag = category[1].trim().toLowerCase();

                    // Add to global categories
                    if (tag in categories) {
                        categories[tag].amount++;
                    } else {
                        categories[tag] = {
                            amount: 1,
                            selected: false
                        };
                    }

                    categories['All'].amount++;

                    categories = categories;
                });

                let productId = newProductInfo.id;

                if (productId in products) {
                    if (products[productId].event.created_at < newProductInfo.event.created_at) {
                        products[productId] = newProductInfo;
                    }
                } else {
                    // If whiteListedStalls is provided, don't limit the number of loaded products
                    // If there is no whiteListedStalls, load just maxProductsLoaded products, unless
                    // maxProductsLoaded is 0 (unlimited)

                    if (
                        whiteListedStalls
                        ||
                        (
                            whiteListedStalls === null
                            &&
                            (
                                (
                                    maxProductsLoaded === 0
                                )
                                ||
                                (
                                    maxProductsLoaded > 0
                                    &&
                                    productsLoaded < maxProductsLoaded
                                )
                            )
                        )
                    ) {
                        products[productId] = newProductInfo;
                        productsLoaded++;
                    }
                }
            });
    });

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
</script>

<!--
<div class="p-2 py-2 pt-8 h-auto container grid align-center mx-auto">
    <div tabindex="0" class="lg:grid mt-3 mb-4 rounded-box collapse collapse-plus border border-gray-400/70 bg-base-100">
        <input type="checkbox" />
        <div class="collapse-title text-xl font-medium align-middle">
            <div class="w-8 h-8">
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

<div class="p-2 py-2 pt-8 h-auto container grid grid-cols-2 2xl:grid-cols-3 3xl:grid-cols-4 gap-4 lg:gap-12 2xl:gap-16 3xl:gap-24 align-center mx-auto" >
    {#each Object.entries(filteredProducts) as [productId, product]}
        {#if (!whiteListedStalls || whiteListedStalls && whiteListedStalls.length === 0) || (whiteListedStalls && whiteListedStalls.length > 0 && whiteListedStalls.includes(product.stall_id))}
            <ProductCard {product} {onImgError} isOnStall={false} bind:viewProductIdOnModal={viewProductIdOnModal} bind:scrollPosition={scrollPosition} />
        {/if}
    {/each}
</div>

<ProductModal bind:viewProductIdOnModal={viewProductIdOnModal} bind:scrollPosition={scrollPosition} />