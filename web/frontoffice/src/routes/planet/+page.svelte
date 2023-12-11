<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    export let maxProductsLoaded: number = 0;   // Unlimited
</script>

<Titleh1 titleClass="p-4 mt-4 md:mt-12 mb-0 text-center text-3xl lg:text-3xl">Plebeian Planet</Titleh1>

<div class="flex">
    <p class="mb-6 text-sm mx-auto">Products created on {import.meta.env.VITE_SITE_NAME}</p>
</div>

<ProductCardBrowser {maxProductsLoaded} showOnlyPMProducts={true} />