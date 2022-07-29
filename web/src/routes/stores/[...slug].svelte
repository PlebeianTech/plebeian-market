<svelte:head>
    <title>Stores</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { storeName: slug } }
    }
</script>

<script lang="ts">
    import { Auction, fromJson } from "$lib/types/auction";
    import StoreView from "$lib/components/StoreView.svelte";
    export let storeName: string;
    let auctions: Auction[] | null = [];

</script>


<StoreView
    loader={{endpoint: `users/${storeName}/auctions`, fromJson}}
    storeName={storeName}
    bind:entities={auctions}
/>
