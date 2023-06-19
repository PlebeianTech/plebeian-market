<script lang="ts">
    import { onMount } from "svelte";
    import ProductCard from "$lib/components/stores/ProductCard.svelte";
    import {getProducts} from "$lib/services/nostr";
    import {filterTags, getFirstTagValue} from "$lib/nostr/utils";
    import {onImgError} from "$lib/shopping";
    import Settings from "$sharedLib/components/icons/Settings.svelte";
    import {refreshStalls} from "$lib/shopping";
    import {getConfigurationFromFile} from "$lib/utils";

    export let whiteListedStalls: string = null;

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
        let config = await getConfigurationFromFile();

        if (config && config.admin_pubkey.length === 64) {
            // admin pubkey specified, so let's wait
            // to give some time for the homepage setup
            // to get here from Nostr relays...
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        refreshStalls();

        getProducts(null, null,
            (productEvent) => {
                let content = JSON.parse(productEvent.content);
                content.event = productEvent;

                if (content.name.toLowerCase().includes('test') || content.description.toLowerCase().includes('test')) {
                    return;
                }

                if (!content.images && !content.image) {
                    return;
                }

                if (!content.id) {
                    let productId = getFirstTagValue(productEvent.tags, 'd');
                    if (productId !== null) {
                        content.id = productId;
                    } else {
                        return;
                    }
                }

                let categoryTags = filterTags(productEvent.tags, 't');
                if (categoryTags.length > 0) {
                    categoryTags.forEach((category) => {
                        let tag = category[1].trim().toLowerCase();

                        // vitamin the product with categories
                        if (content.tags) {
                            content.tags.push(tag);
                        } else {
                            content.tags = [tag];
                        }

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
                }

                let productId = content.id;

                if (productId in products) {
                    if (products[productId].event.created_at < productEvent.created_at) {
                        products[productId] = content;
                    }
                } else {
                    products[productId] = content;
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

<div class="p-2 py-2 pt-8 h-auto container grid align-center mx-auto">
    <div tabindex="0" class="lg:grid mt-3 mb-4 rounded-box collapse collapse-plus border border-gray-400/70 bg-base-100">
        <input type="checkbox" />
        <div class="collapse-title text-xl font-medium align-middle">
            <Settings />

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

<div class="p-2 py-2 pt-8 h-auto container grid lg:grid-cols-3 align-center mx-auto">
    {#each Object.entries(filteredProducts) as [productId, product]}
        {#if (!whiteListedStalls || whiteListedStalls && whiteListedStalls.length === 0) || (whiteListedStalls && whiteListedStalls.length > 0 && whiteListedStalls.includes(product.stall_id))}
            {#if ((product.images && product.images.length > 0) || product.image) }
                <ProductCard {product} {onImgError} isOnStall={false}></ProductCard>
            {/if}
        {/if}
    {/each}
</div>
