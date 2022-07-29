<svelte:head>
    <title>Stores</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { key } = params;
        return { props: { storeName: key } }
    }
</script>

<script lang="ts">
    import StoreNotFound from "$lib/components/StoreNotFound.svelte";
    import StoreView from "$lib/components/StoreView.svelte";
    import { getStore } from "../../lib/services/api";
    import { store } from "../../lib/stores";
    import { onMount } from "svelte";
    export let storeName: string;
    function fetchStore(storeName: string) {
        getStore(storeName, s => {
            store.set(s);
        });
    }

    onMount(async () => {
        fetchStore(storeName);
    });
</script>

{#if storeName == "" || !$store}
    <StoreNotFound />
{:else}
    <StoreView store={$store} />
{/if}
