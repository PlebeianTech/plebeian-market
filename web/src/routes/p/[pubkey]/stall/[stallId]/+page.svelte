<script lang="ts">
    import ProductList from "$lib/components/stores/ProductList.svelte";
    import {onMount} from "svelte";
    import {NostrPool, stalls} from "$lib/stores";
    import {refreshStalls} from "../../../../../lib/shopping";

    /** @type {import('./$types').PageData} */
    export let data;

    onMount(async () => {
        refreshStalls($NostrPool);
    });
</script>

<svelte:head>
    <title>Product Browser</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-8 lg:mb-8 p-4">
    {#if $stalls !== null && $stalls.stalls[data.stallId]}
        {$stalls.stalls[data.stallId].name}
    {:else}
        Products in the store
    {/if}
</h1>

<div class="grid justify-center items-center lg:mx-20 gap-6 place-content-center">
    <ProductList merchantPubkey={data.pubkey} stallId={data.stallId}></ProductList>
</div>
