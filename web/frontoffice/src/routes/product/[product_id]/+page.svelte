<script lang="ts">
    import Product from "$lib/components/stores/Product.svelte";

    /** @type {import('./$types').PageData} */
    export let data;
</script>

<Product {data} />
