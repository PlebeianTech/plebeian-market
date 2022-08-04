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
    let title = "My Stall";
    let cardType;
    let auctions: Auction[] | null = [];
    let viewedAuctions = (localStorage.getItem('auctions-viewed') || "").split(",");

    // NB: the "new" button is shown when there are no auctions that are not ended and not viewed
    // (basically auctions that have been just created and the user didn't go through the whole tweet-start-view flow, *unless* they already ended)
    $: showNewButton = ($user && $user.nym === stallOwnerNym || stallOwnerNym === "") || auctions === null || !auctions.find(a => !a.ended && viewedAuctions.indexOf(a.key) === -1);

    onMount(async () => {
        if (stallOwnerNym === "" || stallOwnerNym === null) {
            goto('/');
        }
        if ($user && $user.nym === stallOwnerNym) {
            title = `${stallOwnerNym}'s Stall`
            cardType = AuctionCard;
        } else {
            cardType = PublicAuctionCard;
        }
    });
</script>

<StallView
    title={title}
    loader={{endpoint: `users/${stallOwnerNym}/auctions`, responseField: 'auctions', fromJson}}
    stallOwnerNym={stallOwnerNym}
    card={cardType}
    editor={AuctionEditor}
    bind:showNewButton={showNewButton}
    bind:entities={auctions}
/>
