<svelte:head>
    <title>Market Stall</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { stallOwnerNym: slug } }
    }
</script>

<script lang="ts">
    import { user } from "$lib/stores";
    import { Auction, fromJson } from "$lib/types/auction";
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import StallView from "$lib/components/StallView.svelte";
    import AuctionCard from "$lib/components/AuctionCard.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import PublicAuctionCard from "$lib/components/PublicAuctionCard.svelte";


    export let stallOwnerNym: string;

    onMount(async () => {
        if (stallOwnerNym === "" || stallOwnerNym === null) {
            goto('/');
        }
    });
</script>

<StallView
    stallOwnerNym={stallOwnerNym}
/>
