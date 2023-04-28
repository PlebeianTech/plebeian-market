<script>
    import ShoppingCart from "$lib/components/stores/ShoppingCart.svelte";
</script>

<svelte:head>
    <title>Shopping Cart</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-12 lg:mb-12 p-4">Shopping Cart</h1>

<div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">
    <ShoppingCart></ShoppingCart>
</div>
