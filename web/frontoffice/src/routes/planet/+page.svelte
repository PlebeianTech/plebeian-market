<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    export let maxProductsLoaded: number = 0;   // Unlimited
</script>

<Titleh1>Plebeian Planet</Titleh1>

<p class="text-3xl">Products created on {import.meta.env.VITE_SITE_NAME}</p>

<ProductCardBrowser {maxProductsLoaded} showOnlyPMProducts={true} />