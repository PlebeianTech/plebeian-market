<script lang="ts">
    import Product from "$lib/components/stores/Product.svelte";

    /** @type {import('./$types').PageData} */
    export let data;
</script>

<Product product_id={data.product_id} />
