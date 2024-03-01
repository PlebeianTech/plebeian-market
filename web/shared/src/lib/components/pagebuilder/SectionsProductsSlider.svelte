<script lang="ts" xmlns="http://www.w3.org/1999/html">
    import {onMount} from "svelte";
    import { browser } from '$app/environment'
    import {
        getProducts,
        EVENT_KIND_AUCTION,
        subscribeConfiguration,
        getConfigurationKey
    } from "$sharedLib/services/nostr";
    import {filterTags} from "$sharedLib/nostr/utils";
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {fileConfiguration, isSuperAdmin} from "$sharedLib/stores";
    import Countdown from "$sharedLib/components/Countdown.svelte";
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import AdminActions from "$sharedLib/components/pagebuilder/AdminActions.svelte";
    import {getItemsFromSection, getHtmlFromRichText} from "$sharedLib/pagebuilder";
    import RichTextComposer from "$sharedLib/components/pagebuilder/lexical-editor/RichTextComposer.svelte";

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
                let productId = newProductInfo.id;
                if (!(productId in products) || (productId in products && products[productId].event.created_at < newProductInfo.event.created_at)) {
                    // Calculate if ended
                    if (newProductInfo.event.kind === EVENT_KIND_AUCTION) {
                        if (newProductInfo.start_date) {
                            now = Math.floor(Date.now() / 1000);
                            let endsAt = newProductInfo.start_date + newProductInfo.duration;
                            newProductInfo.endsAt = endsAt;
                            newProductInfo.ended = now > endsAt;
                        } else {
                            newProductInfo.ended = false;
                        }
                    }

                    products[productId] = newProductInfo;
                }
            },
            async () => {
                // EOSE: all products loaded
                if (browser) {
                    const {Carousel} = await import('tw-elements');

                    // First: destroy
                    const myCarouselEl = document.getElementById('slider_'+pageId+'_'+sectionId);
                    let myCarousel = new Carousel(myCarouselEl);
                    myCarousel.dispose();

                    // Second: create
                    myCarousel = new Carousel(myCarouselEl);
                    myCarousel.cycle();

                    productsLoaded = true;
                }

                if ($fileConfiguration?.admin_pubkeys?.length > 0) {
                    let richTextForProductsConfigurationKeys = [];

                    Object.keys(products).forEach(productId => {
                        richTextForProductsConfigurationKeys.push(getConfigurationKey('section_products_with_slider_' + pageId + '_' + sectionId + '_' + productId));
                    });

                    subscribeConfiguration($fileConfiguration.admin_pubkeys, richTextForProductsConfigurationKeys,
                        (richTextForProduct, rcAt, e) => {
                            let productConfigKeyForThisEvent = filterTags(e.tags, 'd').join()
                            let productIdForThisConfigurantionEvent = productConfigKeyForThisEvent.split('_').at(-1);

                            if (
                                productIdForThisConfigurantionEvent &&
                                (
                                    !products[productIdForThisConfigurantionEvent].richTextReceivedAt ||
                                    (
                                        products[productIdForThisConfigurantionEvent].richTextReceivedAt &&
                                        rcAt > products[productIdForThisConfigurantionEvent].richTextReceivedAt
                                    )
                                )
                            ) {
                                products[productIdForThisConfigurantionEvent].richTextReceivedAt = rcAt;
                                products[productIdForThisConfigurantionEvent].richText = richTextForProduct;
                            }
                        });
                }
            });
    });
</script>

<main class="p-4 mx-auto">
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
                        <div class="h-full max-h-[20rem] md:max-h-[36rem] w-auto md:w-6/12 overflow-hidden">
                            <a href="/product/{product.id}">
                                <img class="w-auto max-h-full mx-auto p-4 md:p-6" alt="{product.name ?? 'Product #' + i}"
                                     src="{product.images ? product.images[0] : product.image ?? productImageFallback}"/>
                            </a>
                        </div>

                        <div class="w-full md:w-6/12 overflow-hidden p-4 pt-0 md:p-16 md:pt-4 md:pl-12 md:text-lg">
                            <div class="z-[300] prose prose-p:my-2 md:prose-p:my-0">
                                {#if product.richText}
                                    <RichTextComposer initialMinifiedLexicalContent={product.richText} editable={false} />
                                {:else}
                                    {#if product.name}
                                        <h2 class="md:text-3xl mb-1 md:mb-2">{product.name}</h2>
                                    {/if}
                                    {#if product.description}
                                        {@html getHtmlFromRichText(product.description)}
                                    {/if}
                                {/if}
                            </div>

                            {#if product.event.kind === EVENT_KIND_AUCTION}
                                {#if !product.start_date}
                                    <div class="flex">
                                        <p class="pt-5 text-xl font-bold mx-auto">Coming Soon</p>
                                    </div>
                                {:else}
                                    {#if product.ended}
                                        <div class="flex">
                                            <p class="pt-5 text-xl font-bold mx-auto">Auction Ended</p>
                                        </div>
                                    {:else}
                                        <div class="pt-4 pb-2">
                                            <Countdown totalSeconds={product.endsAt - now} bind:ended={product.ended} />
                                        </div>
                                    {/if}
                                {/if}
                            {/if}

                            <a class="btn btn-outline btn-accent mt-6" href="/product/{product.id}">View product</a>
                            {#if $isSuperAdmin}
                                <button class="btn btn-outline btn-primary mt-6 ml-4" on:click={() => setupSection(pageId, sectionId, product, true)}>Edit text</button>

                                <div class="p-0 md:p-4 md:pb-0">
                                    <AdminActions
                                        itemId={product.id}
                                        entityName="products"
                                    />
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>
            {/each}

            <!-- CTA Slider -->
            {#if Object.entries(products).length > 1 && $fileConfiguration.backend_present}
                <div class="hidden h-[36rem] max-h-full w-full relative float-left -mr-[100%] bg-base-200/40 rounded-xl !transform-none opacity-0 transition-opacity duration-[600ms] ease-in-out motion-reduce:transition-none"
                     data-te-carousel-fade
                     data-te-carousel-item>
                    <div class="relative h-full w-auto md:flex qaaaoverflow-hidden">
                        <div class="h-full max-h-[20rem] md:max-h-[36rem] w-auto md:w-6/12 overflow-hidden">
                            <a class="flex" rel="external" href="/admin">
                                <span class="w-7/12 max-h-20 mt-6 md:mt-12 mx-auto text-green-500 tooltip">
                                    <Plus />
                                </span>
                            </a>
                        </div>

                        <div class="w-full md:w-6/12 overflow-hidden p-4 pt-0 md:p-16 md:pt-4 md:pl-12 md:text-lg">
                            <div class="z-[300] prose lg:prose-xl prose-p:my-2 md:prose-p:my-3">
                                <h2 class="md:text-3xl mb-1 md:mb-2">Sell or auction your product here!</h2>
                                <p>Create your stall and start selling or auctioning your products in 5 minutes!</p>
                            </div>

                            <a class="btn btn-outline btn-accent mt-6" rel="external" href="/admin">Sell your products</a>
                        </div>
                    </div>
                </div>
            {/if}
        </div>

        {#if Object.entries(products).length > 1}
            <!-- Carousel controls - prev item-->
            <div class="absolute bottom-0 left-0 top-0 z-[1] flex w-[3%] items-center justify-center">
                <span class="absolute -mr-10 bg-white rounded-full shadow-gray-500 shadow-md hover:shadow-lg h-12 w-12 text-3xl flex items-center justify-center
                            border-0 opacity-70 transition-opacity duration-150 ease-[cubic-bezier(0.25,0.1,0.25,1.0)] hover:no-underline
                            hover:opacity-90 hover:outline-none focus:no-underline focus:opacity-90 motion-reduce:transition-none
                            text-indigo-600 hover:text-indigo-400 focus:text-indigo-400 focus:outline-none focus:shadow-outline cursor-pointer"
                      data-te-target="#slider_{pageId}_{sectionId}"
                      data-te-slide="prev"><span style="transform: scale(-1);">&#x279c;</span></span>
            </div>
            <!-- Carousel controls - next item-->
            <div class="absolute bottom-0 right-0 top-0 z-[1] flex w-[3%] items-center justify-center">
                <span class="absolute -ml-10 bg-white rounded-full shadow-gray-500 shadow-md hover:shadow-lg h-12 w-12 text-3xl flex items-center justify-center
                            border-0 opacity-70 transition-opacity duration-150 ease-[cubic-bezier(0.25,0.1,0.25,1.0)] hover:no-underline
                            hover:opacity-90 hover:outline-none focus:no-underline focus:opacity-90 motion-reduce:transition-none
                            text-indigo-600 hover:text-indigo-400 focus:text-indigo-400 focus:outline-none focus:shadow-outline cursor-pointer"
                      style="transform: scale(1);"
                      data-te-target="#slider_{pageId}_{sectionId}"
                      data-te-slide="next">&#x279c;</span>
            </div>

            <div class="inset-x-0 p-0 mt-3 mx-[5%] md:mx-[15%] md:mt-6 mb-4 z-[2] flex list-none justify-center" data-te-carousel-indicators>
                {#each Object.entries(products) as [_, product], i}
                    <button data-te-target="#slider_{pageId}_{sectionId}"
                            data-te-slide-to="{i}"
                            data-te-carousel-active={i === 0 ? true : null}
                            class="px-2 md:px-12 opacity-50 hover:opacity-100">
                        <img class="w-full max-h-16" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" alt="">
                    </button>
                {/each}

                <!-- CTA Slider -->
                {#if Object.entries(products).length > 1 && $fileConfiguration.backend_present}
                    <button data-te-target="#slider_{pageId}_{sectionId}"
                            data-te-slide-to="{Object.entries(products).length}"
                            class="mx-1 md:mx-8 w-16 opacity-50 hover:opacity-100 text-green-500 tooltip">
                        <Plus />
                    </button>
                {/if}
            </div>
        {/if}
    </div>
</main>
