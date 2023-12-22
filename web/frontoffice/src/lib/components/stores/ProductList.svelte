<script lang="ts">
    import {EVENT_KIND_AUCTION, EVENT_KIND_PRODUCT, getProducts} from "$sharedLib/services/nostr";
    import ProductCard from "$lib/components/stores/ProductCard.svelte";
    import ProductRow from "$lib/components/stores/ProductRow.svelte";
    import {getFirstTagValue, newNostrConversation} from "$sharedLib/nostr/utils";
    import {onImgError} from "$lib/shopping";
    import ViewList from "$sharedLib/components/icons/ViewList.svelte";
    import ViewCards from "$sharedLib/components/icons/ViewCards.svelte";
    import EmailIcon from "$sharedLib/components/icons/Email.svelte";
    import EyeSlash from "$sharedLib/components/icons/Eye-slash.svelte";
    import Eye from "$sharedLib/components/icons/Eye.svelte";
    import { afterNavigate } from "$app/navigation";
    import ProductModal from "$lib/components/stores/ProductModal.svelte";

    export let merchantPubkey: string;
    export let stallId: string;

    let products: {[productId: string]: {}} = {};
    let viewProductIdOnModal: string | null = null;
    let scrollPosition: number | null = null;

    let listView = false;
    let showExpiredAuctions: boolean = false;

    afterNavigate(() => {
        products = {};

        getProducts(merchantPubkey, null,
            (newProductInfo) => {
                if (newProductInfo.stall_id === stallId) {
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
                }
            });
    });
</script>

<div class="join join-vertical lg:join-horizontal justify-end">
    <button class="btn join-item gap-2" on:click={() => newNostrConversation(merchantPubkey)}>
        <span class="w-8 h-8">
            <EmailIcon />
        </span>
        Contact the merchant
    </button>
    <div class="divider divider-horizontal hidden md:block"></div>
    <button class="btn join-item hidden md:block tooltip" data-tip="{showExpiredAuctions ? 'Hide expired auctions' : 'Show expired auctions'}" class:btn-active={showExpiredAuctions} on:click={() => showExpiredAuctions = !showExpiredAuctions}>
        {#if showExpiredAuctions}
            <Eye />
        {:else}
            <EyeSlash />
        {/if}
    </button>
    <div class="divider divider-horizontal hidden md:block"></div>
    <button class="btn join-item hidden md:block" class:btn-active={listView} on:click={() => listView = true}>
        <ViewList />
    </button>
    <button class="btn join-item hidden md:block" class:btn-active={!listView} on:click={() => listView = false}>
        <ViewCards />
    </button>
</div>

{#if listView}
    <table class="table table-auto table-zebra w-full place-content-center justify-center text-center">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Type</th>
                <th>Stock</th>
                <th>Price</th>
                <th>Image</th>
                <th></th>
            </tr>
        </thead>

        <tbody>
            {#each Object.entries(products) as [productId, product]}
                {#if product.event.kind === EVENT_KIND_PRODUCT || (product.event.kind === EVENT_KIND_AUCTION && (showExpiredAuctions || !showExpiredAuctions && product.ended === false) )}
                    <ProductRow {product} {onImgError}></ProductRow>
                {/if}
            {/each}
        </tbody>
    </table>
{:else}
    <div class="p-2 py-2 pt-1 h-auto container grid lg:grid-cols-2 2xl:grid-cols-3 3xl:grid-cols-4 gap-6 lg:gap-12 2xl:gap-16 3xl:gap-24 place-content-center">
        {#each Object.entries(products) as [productId, product]}
            {#if product.event.kind === EVENT_KIND_PRODUCT || (product.event.kind === EVENT_KIND_AUCTION && (showExpiredAuctions || !showExpiredAuctions && product.ended === false) )}
                <ProductCard {product} {onImgError} isOnStall={true} bind:viewProductIdOnModal={viewProductIdOnModal} bind:scrollPosition={scrollPosition} />
            {/if}
        {/each}
    </div>

    <ProductModal bind:viewProductIdOnModal={viewProductIdOnModal} bind:scrollPosition={scrollPosition} />
{/if}
