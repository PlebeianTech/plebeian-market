<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { onMount } from "svelte";
    import Typewriter from "$lib/components/Typewriter.svelte";
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import {getBaseUrl} from "../lib/utils";
    import GoldenGai from "$lib/images/golden-gai-tokyo.jpg";
    import ProductCard from "../lib/components/stores/ProductCard.svelte";
    import {subscribeProducts} from "../lib/services/nostr";
    import {filterTags, getFirstTagValue} from "../lib/nostr/utils";
    import {NostrPool} from "../lib/stores";
    import {addToCart, onImgError, onQtyChangeClick} from "../lib/services/shopping";

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

    $: categoriesSelected = Object.keys( Object.fromEntries( Object.entries(categories).filter(([category_id, category]) => {
        return category.selected;
    }) ) );

    interface ProductsAssociativeArray {
        [key: string]: {}
    }
    let products: ProductsAssociativeArray[] = [];   // : {[product_id: string]: {}} = {};

    $: filteredProducts = Object.fromEntries( Object.entries(products).filter(([product_id, product]) => {
        if (categories['All'].selected) {
            return true;
        } else {
            for (var i = 0; i < categoriesSelected.length; i++) {
                let categorySelected = categoriesSelected[i];

                if (product.tags && product.tags.includes(categorySelected)) {
                    return true;
                }
            }
        }
    }) );

    onMount(async () => {
        subscribeProducts($NostrPool, null,
            (productEvent) => {
                let content = JSON.parse(productEvent.content);

                if (!content.images && !content.image) {
                    return;
                }

                content.created_at = productEvent.created_at;
                content.merchantPubkey = productEvent.pubkey;

                if (!content.id) {
                    let product_id = getFirstTagValue(productEvent.tags, 'd');

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

                    if (product_id !== null) {
                        content.id = product_id;
                    } else {
                        return;
                    }
                }

                let product_id = content.id;

                if (product_id in products) {
                    if (products[product_id].createdAt < productEvent.created_at) {
                        products[product_id] = content;
                    }
                } else {
                    products[product_id] = content;
                }

                // console.log('products', products);
            });
    });

    function toggleCategory(category) {
        if (category === 'All') {
            for (const cat in categories) {
                if (cat !== 'All') {
                    categories[cat].selected = false;
                }
            }
        } else {
            categories['All'].selected = false;
        }
    }
</script>

<MetaTags
        title="Plebeian Market"
        description="Plebeian Market is a distributed self sovereign P2P market place."
        openGraph={{
            site_name: import.meta.env.VITE_SITE_NAME,
            type: "website",
            url: $page.url.href,
            title: "Plebeian Market",
            description: "Plebeian Market is a distributed self sovereign P2P market place.",
            images: [
              {
                url: getBaseUrl() + "images/Plebeian_Logo_OpenGraph.png",
                alt: "Plebeian Market logo"
              }
            ],
        }}
        twitter={{
            site: import.meta.env.VITE_TWITTER_USER,
            handle: import.meta.env.VITE_TWITTER_USER,
            cardType: "summary_large_image",
            image: getBaseUrl() + "images/Plebeian_Logo_OpenGraph.png",
            imageAlt: "Plebeian Market logo",
        }}
/>

<div class="bg-no-repeat bg-center bg-cover" style="background-image: url('{GoldenGai}')">
  <div class="bg-gradient-to-r from-zinc-900 to-zinc-900/40">
    <div class="grid lg:w-2/3 mx-auto py-12">
      <div class="grid lg:place-items-start place-items-center py-8 px-8">
          <div class="">
            <Typewriter />
          </div>
      </div>
    </div>
  </div>
</div>

<div class="p-2 py-2 pt-8 h-auto container grid align-center mx-auto">
    <div tabindex="0" class="lg:grid mt-3 mb-4 collapse-open rounded-box collapse collapse-plus border border-gray-400/70 bg-base-100">
        <input type="checkbox" />
        <div class="collapse-title text-l font-medium">
            Filter:
            {#if categoriesSelected.length > 0}
                Selected =>
                {#each categoriesSelected as category}
                    <span class="align-baseline text-xl">{category}, </span>
                {/each}
            {/if}
        </div>
        <div class="collapse-content columns-4">
            {#each Object.entries(categories) as [category, data]}
                <div class="label justify-normal mb-3">
                    <input type="checkbox" bind:checked={data.selected} on:change={() => toggleCategory(category)} class="checkbox checkbox-md mr-3" />
                    <span class="align-baseline text-xl">{category}</span> <span class="ml-2 text-sm">({data.amount})</span>
                </div>
            {/each}
        </div>
    </div>
</div>

<div class="p-2 py-2 pt-8 h-auto container grid lg:grid-cols-3 align-center mx-auto">
    {#each Object.entries(filteredProducts) as [product_id, product]}
        {#if (product.images || product.image) }
            <ProductCard {product} {addToCart} {onImgError} {onQtyChangeClick}></ProductCard>
        {/if}
    {/each}
</div>
