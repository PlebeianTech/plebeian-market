<script lang="ts">
    import Product from "$lib/components/stores/Product.svelte";

    /** @type {import('./$types').PageData} */
    export let data;
</script>

{#key data.product_id}
    <Product product_id={data.product_id} />
{/key}