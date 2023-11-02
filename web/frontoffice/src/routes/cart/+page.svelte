<script lang="ts">
    import ShoppingCart from "$lib/components/stores/ShoppingCart.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
</script>

<svelte:head>
    <title>Shopping Cart</title>
</svelte:head>

<Titleh1>Shopping Cart</Titleh1>

<ShoppingCart compact={false} />
