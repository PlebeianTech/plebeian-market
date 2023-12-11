<script lang="ts" xmlns="http://www.w3.org/1999/html">
    import {onMount} from "svelte";
    import { browser } from '$app/environment'
    import {getItemsFromSection} from "$lib/pagebuilder";
    import {
        getProducts,
        EVENT_KIND_AUCTION,
        EVENT_KIND_PRODUCT,
        subscribeConfiguration, getConfigurationKey
    } from "$sharedLib/services/nostr";
    import {filterTags, getFirstTagValue} from "$sharedLib/nostr/utils";
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {isSuperAdmin} from "$sharedLib/stores";
    import {getConfigurationFromFile} from "$sharedLib/utils";
    import SvelteMarkdown from "svelte-markdown";
    import Countdown from "$sharedLib/components/Countdown.svelte";

    export let pageId;
    export let sectionId;
    export let setupSection;

    let now = Math.floor(Date.now() / 1000);

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

                let productId = newProductInfo.id;
                if (!(productId in products) || (productId in products && products[productId].event.created_at < newProductInfo.event.created_at)) {
                    // Calculate if ended
                    if (newProductInfo.event.kind === EVENT_KIND_AUCTION) {
                        now = Math.floor(Date.now() / 1000);
                        let endsAt = newProductInfo.start_date + newProductInfo.duration;
                        newProductInfo.endsAt = endsAt;
                        newProductInfo.ended = now > endsAt;
                    }

                    products[productId] = newProductInfo;
                }
            },
            async () => {
                // EOSE: all products loaded
                if (browser) {
                    const {Carousel, initTE} = await import('tw-elements');
                    //await new Promise(resolve => setTimeout(resolve, 2000));
                    initTE({Carousel});
                    productsLoaded = true;
                }

                let config = await getConfigurationFromFile();
                if (config && config.admin_pubkeys.length > 0) {
                    let markdownTextForProductsConfigurationKeys = [];

                    Object.keys(products).forEach(productId => {
                        markdownTextForProductsConfigurationKeys.push(getConfigurationKey('section_products_with_slider_' + pageId + '_' + sectionId + '_' + productId));
                    });

                    subscribeConfiguration(config.admin_pubkeys, markdownTextForProductsConfigurationKeys,
                        (markdownTextForProduct, rcAt, e) => {
                            let productConfigKeyForThisEvent = filterTags(e.tags, 'd').join()
                            let productIdForThisConfigurantionEvent = productConfigKeyForThisEvent.split('_').at(-1);

                            if (
                                productIdForThisConfigurantionEvent &&
                                (
                                    !products[productIdForThisConfigurantionEvent].markdownReceivedAt ||
                                    (
                                        products[productIdForThisConfigurantionEvent].markdownReceivedAt &&
                                        rcAt > products[productIdForThisConfigurantionEvent].markdownReceivedAt
                                    )
                                )
                            ) {
                                products[productIdForThisConfigurantionEvent].markdownReceivedAt = rcAt;
                                products[productIdForThisConfigurantionEvent].markdownText = markdownTextForProduct;
                            }
                        });
                }
            });
    });
</script>

<main class="p-4 md:container mx-auto">
    {#if !productsLoaded}
        <div class="p-12 flex flex-wrap items-center justify-center">
            <span class="loading loading-bars w-24"></span>
        </div>
    {/if}

    <div id="slider_{pageId}_{sectionId}"
         class="w-full" class:hidden={!productsLoaded}
         data-te-carousel-init
         data-te-ride="carousel">

        <!-- Carousel items -->
        <div class="w-full h-[36rem] overflow-hidden">
            {#each Object.entries(products) as [_, product], i}
                <div class="h-[36rem] max-h-full w-full relative float-left -mr-[100%] bg-base-200/40 rounded-xl !transform-none opacity-0 transition-opacity duration-[600ms] ease-in-out motion-reduce:transition-none"
                     class:hidden={i > 0}
                     data-te-carousel-fade
                     data-te-carousel-item
                     data-te-carousel-active={i === 0 ? true : null}>
                    <div class="relative h-full w-auto md:flex overflow-hidden">
                        <div class="w-full md:w-6/12 overflow-hidden">
                            <img class="h-full w-auto mx-auto p-4 md:p-6" alt="{product.name ?? 'Product #' + i}"
                                 src="{product.images ? product.images[0] : product.image ?? productImageFallback}"/>
                        </div>

                        <div class="w-full md:w-6/12 overflow-hidden p-4 md:p-16 md:pl-12 md:text-lg">
                            <div class="z-[300] prose lg:prose-xl">
                                {#if product.markdownText}
                                    <SvelteMarkdown source={product.markdownText} />
                                {:else}
                                    {#if product.name}
                                        <h2 class="md:text-3xl mb-8 prose lg:prose-xl">{product.name}</h2>
                                    {/if}
                                    {#if product.description}
                                        <SvelteMarkdown source={product.description} />
                                    {/if}
                                {/if}
                            </div>

                            {#if product.event.kind === EVENT_KIND_AUCTION}
                                {#if product.ended}
                                    <div class="flex">
                                        <p class="py-5 text-xl font-bold mx-auto">Auction Ended</p>
                                    </div>
                                {:else}
                                    <div class="pt-4 pb-2">
                                        <Countdown totalSeconds={product.endsAt - now} bind:ended={product.ended} />
                                    </div>
                                {/if}
                            {/if}

                            <a class="btn btn-outline btn-accent mt-6" href="/product/{product.id}">View product</a>
                            {#if $isSuperAdmin}
                                <button class="btn btn-outline btn-primary mt-6 ml-4" on:click={() => setupSection(pageId, sectionId, product, true)}>Edit text</button>
                            {/if}
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        {#if Object.entries(products).length > 1}
            <!-- Carousel controls - prev item-->
            <div class="absolute bottom-0 left-0 top-0 z-[1] flex w-[3%] items-center justify-center">
                <span class="absolute -mr-6 bg-white rounded-full shadow-gray-500 shadow-md hover:shadow-lg h-12 w-12 text-3xl flex items-center justify-center
                            border-0 opacity-70 transition-opacity duration-150 ease-[cubic-bezier(0.25,0.1,0.25,1.0)] hover:no-underline
                            hover:opacity-90 hover:outline-none focus:no-underline focus:opacity-90 motion-reduce:transition-none
                            text-indigo-600 hover:text-indigo-400 focus:text-indigo-400 focus:outline-none focus:shadow-outline cursor-pointer"
                      data-te-target="#slider_{pageId}_{sectionId}"
                      data-te-slide="prev"><span style="transform: scale(-1);">&#x279c;</span></span>
            </div>
            <!-- Carousel controls - next item-->
            <div class="absolute bottom-0 right-0 top-0 z-[1] flex w-[3%] items-center justify-center">
                <span class="absolute -ml-6 bg-white rounded-full shadow-gray-500 shadow-md hover:shadow-lg h-12 w-12 text-3xl flex items-center justify-center
                            border-0 opacity-70 transition-opacity duration-150 ease-[cubic-bezier(0.25,0.1,0.25,1.0)] hover:no-underline
                            hover:opacity-90 hover:outline-none focus:no-underline focus:opacity-90 motion-reduce:transition-none
                            text-indigo-600 hover:text-indigo-400 focus:text-indigo-400 focus:outline-none focus:shadow-outline cursor-pointer"
                      style="transform: scale(1);"
                      data-te-target="#slider_{pageId}_{sectionId}"
                      data-te-slide="next">&#x279c;</span>
            </div>

            <div class="inset-x-0 mt-6 z-[2] mx-[15%] mb-4 flex list-none justify-center p-0" data-te-carousel-indicators>
                {#each Object.entries(products) as [_, product], i}
                    <button data-te-target="#slider_{pageId}_{sectionId}"
                            data-te-slide-to="{i}"
                            data-te-carousel-active={i === 0 ? true : null}
                            class="px-6 md:px-12 opacity-50 hover:opacity-100">
                        <img class="w-full" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" alt="" style="max-height: 60px;">
                    </button>
                {/each}
            </div>
        {/if}
    </div>
</main>
