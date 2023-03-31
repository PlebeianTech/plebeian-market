<script lang="ts">
    import ListProducts from "$lib/components/stores/ListProducts.svelte";
    import Back from "$lib/components/icons/Back.svelte";

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
        <a class="btn btn-primary btn-outline" href="/store_browser">
            <Back />
            Back to the Store Browser
        </a>
    </div>
    -->

    <ListProducts merchant_pubkey={data.pubkey} stall_id={data.stall_id}></ListProducts>
</div>
