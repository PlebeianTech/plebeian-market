<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    export let maxProductsLoaded: number = 0;   // Unlimited
</script>

<Titleh1>Planet</Titleh1>

<ProductCardBrowser {maxProductsLoaded} />