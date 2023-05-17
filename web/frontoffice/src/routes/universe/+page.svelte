<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
</script>

<Titleh1>Universe</Titleh1>

<ProductCardBrowser />
