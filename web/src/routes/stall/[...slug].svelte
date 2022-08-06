<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { stallName: slug } }
    }
</script>

<script lang="ts">
    import { user, Info } from "$lib/stores";
    import { Auction, fromJson } from "$lib/types/auction";
    import StallView from "$lib/components/StallView.svelte";
    import ListView from "$lib/components/ListView.svelte";
    import AuctionCard from "$lib/components/AuctionCard.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import { browser } from "$app/env";

    export let stallName: string;
    let auctions: Auction[] | null = [];
    let viewedAuctions = (browser && localStorage.getItem('auctions-viewed') || "").split(",");

    // NB: the "new" button is shown when there are no auctions that are not ended and not viewed
    // (basically auctions that have been just created and the user didn't go through the whole tweet-start-view flow, *unless* they already ended)
    $: showNewButton = auctions === null || !auctions.find(a => !a.ended && viewedAuctions.indexOf(a.key) === -1);

    function onCreated() {
        user.update((u) => { u!.hasAuctions = true; return u; });
        Info.set("Your auction will start when we verify your tweet!");
    }

    function onView(auction) {
        // NB: using assignement rather than .push() to trigger recalculation of showNewButton
        viewedAuctions = [...viewedAuctions, auction.key];
    }

</script>


{#if $user && $user.nym === stallName || stallName === ""}
    <ListView
        title="My Stall"
        loader={{endpoint: 'auctions', fromJson}} newEntity={() => new Auction()}
        card={AuctionCard} editor={AuctionEditor} bind:showNewButton={showNewButton}
        {onCreated} {onView}
        bind:entities={auctions}>
    </ListView>
{:else}
    <StallView
        loader={{endpoint: `users/${stallName}/auctions`, responseField: 'auctions', fromJson}}
        stallName={stallName}
        bind:entities={auctions}
    />
{/if}