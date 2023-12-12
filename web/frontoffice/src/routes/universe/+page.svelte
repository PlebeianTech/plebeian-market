<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    import Search from "$sharedLib/components/icons/Search.svelte";
    import {fileConfiguration} from "$sharedLib/stores";

    export let maxProductsLoaded: number = 2; // 42   // Unlimited

    let filter = null;
    let showOnlyProductsFromThisCommunity = false;
    let showFixedPriceProducts = true;
    let showAuctions = true;
</script>

<Titleh1 titleClass="p-4 mt-4 md:mt-12 mb-0 text-center text-3xl lg:text-3xl">Nostr Universe</Titleh1>

<div class="flex">
    <p class="mb-6 text-sm mx-auto">Nostr nip-15 compliant products</p>
</div>

<div class="flex flex-col sm:flex-row md:my-2 mb-6 sm:mb-3">
    <div class="relative">
        <span class="h-full absolute inset-y-0 left-0 flex items-center pl-2">
            <Search />
        </span>
        <input bind:value={filter} placeholder="Search product title, description or enter a product id"
               class="block pl-9 pr-4 py-2 w-full md:w-96 rounded border border-gray-400 text-sm focus:outline-none" />
    </div>
</div>

{#if $fileConfiguration.backend_present}
    <div>
        <input type="checkbox" bind:checked={showOnlyProductsFromThisCommunity}/>
        Shown only products from this community
    </div>
{/if}

<div>
    <input type="checkbox" bind:checked={showFixedPriceProducts}/>
    Shown fixed price products
</div>

<div>
    <input type="checkbox" bind:checked={showAuctions}/>
    Shown auctions
</div>

<ProductCardBrowser
    {maxProductsLoaded}
    {filter}
    {showOnlyProductsFromThisCommunity}
    {showFixedPriceProducts}
    {showAuctions}
/>
