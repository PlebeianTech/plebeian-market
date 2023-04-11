<script lang="ts">
    import ProductList from "$lib/components/stores/ProductList.svelte";

    /** @type {import('./$types').PageData} */
    export let data;
</script>

<svelte:head>
    <title>Product Browser</title>
</svelte:head>



<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-8 lg:mb-8 p-4">Products in the store</h1>

<div class="grid justify-center items-center lg:mx-20 gap-6 place-content-center">
    <!--
    <div class="flex items-center mt-4 h-15 gap-8">
        <a class="btn btn-primary btn-outline" href="/stalls">
            <Back />
            Back to the Stall Browser
        </a>
    </div>
    -->

    <ProductList merchantPubkey={data.pubkey} stallId={data.stallId}></ProductList>
</div>
