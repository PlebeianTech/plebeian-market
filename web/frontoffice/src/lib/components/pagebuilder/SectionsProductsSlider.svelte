<script lang="ts">
    import {onMount} from "svelte";
    import { browser } from '$app/environment'
    import {getItemsFromSection} from "$lib/pagebuilder";
    import {getProducts, EVENT_KIND_AUCTION, EVENT_KIND_PRODUCT} from "$sharedLib/services/nostr";
    import {getFirstTagValue} from "$sharedLib/nostr/utils";
    import productImageFallback from "$lib/images/product_image_fallback.svg";

    export let pageId;
    export let sectionId;

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
            async () => {
                if (browser) {
                    const {Carousel, initTE} = await import('tw-elements');
                    //await new Promise(resolve => setTimeout(resolve, 2000));
                    initTE({Carousel});
                    productsLoaded = true;
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

    <div id="carouselDarkVariant"
         class="relative" class:hidden={!productsLoaded}
         data-te-carousel-init
         data-te-ride="carousel">

        <!-- Carousel indicators -->
        <div class="absolute inset-x-0 mt-6 z-[2] mx-[15%] mb-4 flex list-none justify-center p-0" data-te-carousel-indicators>
            {#each Object.entries(products) as [_, product], i}
                {#if product.event.kind === EVENT_KIND_PRODUCT || (product.event.kind === EVENT_KIND_AUCTION && product.ended === false )}
                    <button data-te-target="#carouselDarkVariant"
                            data-te-slide-to="{i}"
                            data-te-carousel-active={i === 0 ? true : null}
                            class="mx-[3px] box-content h-[3px] w-[30px] flex-initial cursor-pointer border-0 border-y-[10px]
                                border-solid border-transparent bg-black bg-clip-padding p-0 -indent-[999px] opacity-50
                                transition-opacity duration-[600ms] ease-[cubic-bezier(0.25,0.1,0.25,1.0)] motion-reduce:transition-none"
                            aria-current="true"
                            aria-label="Slide 1"></button>
                {/if}
            {/each}
        </div>

        <!-- Carousel items -->
        <div class="relative w-full overflow-hidden after:clear-both after:block after:content-[''] max-h-[32rem]">
            {#each Object.entries(products) as [productId, product], i}
                {#if product.event.kind === EVENT_KIND_PRODUCT || (product.event.kind === EVENT_KIND_AUCTION && product.ended === false )}
                    <div class="relative float-left -mr-[100%] w-full !transform-none opacity-0 transition-opacity duration-[600ms] ease-in-out motion-reduce:transition-none"
                         class:hidden={i > 0}
                         data-te-carousel-fade
                         data-te-carousel-item
                         data-te-carousel-active={i === 0 ? true : null}>

                        <div class="block md:flex bg-base-300 rounded-xl h-full max-h-full">
                            <div class="w-full md:w-6/12 h-full max-h-full">
                                <img class="block p-4 md:p-5 md:pr-4 " alt="{product.name ?? 'Product #' + i}"
                                     src="{product.images ? product.images[0] : product.image ?? productImageFallback}"/>
                            </div>

                            <div class="w-full md:w-6/12 p-4 md:p-20 md:pl-12 md:text-lg">
                                {#if product.name}
                                    <h2 class="md:text-3xl mb-8">
                                        <a class="cursor-pointer hover:underline" href="/product/{product.id}">{product.name}</a>
                                    </h2>
                                {/if}
                                {#if product.description}
                                    <p class="md:text-xl">
                                        <a class="cursor-pointer hover:underline" href="/product/{product.id}">{product.description}</a>
                                    </p>
                                {/if}

                                <button class="btn btn-outline btn-info mt-6">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                                    View product
                                </button>
                            </div>
                        </div>
                    </div>
                {/if}
            {/each}
        </div>

        <!-- Carousel controls - prev item-->
        <div class="absolute bottom-0 left-0 top-0 z-[1] flex w-[3%] items-center justify-center">
            <span class="absolute -mr-6 bg-white rounded-full shadow-gray-500 shadow-md hover:shadow-lg h-12 w-12 text-3xl flex items-center justify-center
                        border-0 opacity-70 transition-opacity duration-150 ease-[cubic-bezier(0.25,0.1,0.25,1.0)] hover:no-underline
                        hover:opacity-90 hover:outline-none focus:no-underline focus:opacity-90 motion-reduce:transition-none
                        text-indigo-600 hover:text-indigo-400 focus:text-indigo-400 focus:outline-none focus:shadow-outline cursor-pointer"
                  data-te-target="#carouselDarkVariant"
                  data-te-slide="prev"><span style="transform: scale(-1);">&#x279c;</span></span>
        </div>

        <!-- Carousel controls - next item-->
        <div class="absolute bottom-0 right-0 top-0 z-[1] flex w-[3%] items-center justify-center">
            <span class="absolute -ml-6 bg-white rounded-full shadow-gray-500 shadow-md hover:shadow-lg h-12 w-12 text-3xl flex items-center justify-center
                        border-0 opacity-70 transition-opacity duration-150 ease-[cubic-bezier(0.25,0.1,0.25,1.0)] hover:no-underline
                        hover:opacity-90 hover:outline-none focus:no-underline focus:opacity-90 motion-reduce:transition-none
                        text-indigo-600 hover:text-indigo-400 focus:text-indigo-400 focus:outline-none focus:shadow-outline cursor-pointer"
                  style="transform: scale(1);"
                  data-te-target="#carouselDarkVariant"
                  data-te-slide="next">&#x279c;</span>
        </div>
    </div>
</main>
