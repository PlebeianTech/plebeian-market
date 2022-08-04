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
    import { user, Info } from "$lib/stores";
    import { Auction, fromJson } from "$lib/types/auction";
    import StallView from "$lib/components/StallView.svelte";
    import AuctionCard from "$lib/components/AuctionCard.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import PublicAuctionCard from "$lib/components/PublicAuctionCard.svelte";

    export let stallOwnerNym: string;
    let auctions: Auction[] | null = [];
    let viewedAuctions = (localStorage.getItem('auctions-viewed') || "").split(",");

    // NB: the "new" button is shown when there are no auctions that are not ended and not viewed
    // (basically auctions that have been just created and the user didn't go through the whole tweet-start-view flow, *unless* they already ended)
    $: showNewButton = ($user && $user.nym === stallOwnerNym || stallOwnerNym === "") || auctions === null || !auctions.find(a => !a.ended && viewedAuctions.indexOf(a.key) === -1);

    function onCreated() {
        user.update((u) => { u!.hasAuctions = true; return u; });
        Info.set("Your auction will start when we verify your tweet!");
    }

    function onView(auction) {
        // NB: using assignement rather than .push() to trigger recalculation of showNewButton
        viewedAuctions = [...viewedAuctions, auction.key];
    }

</script>


{#if $user && $user.nym === stallOwnerNym || stallOwnerNym === ""}
    <!-- User viewing own store -->
    <StallView
        title="My Stall"
        loader={{endpoint: 'auctions', responseField: 'auctions', fromJson}}
        newEntity={() => new Auction()}
        stallOwnerNym={stallOwnerNym}
        card={AuctionCard}
        {onCreated} {onView}
        editor={AuctionEditor}
        bind:showNewButton={showNewButton}
        bind:entities={auctions}
    />
{:else}
    <!-- User viewing another user's store -->
    <StallView
        title="My Stall"
        loader={{endpoint: `users/${stallOwnerNym}/auctions`, responseField: 'auctions', fromJson}}
        newEntity={() => new Auction()}
        stallOwnerNym={stallOwnerNym}
        card={PublicAuctionCard}
        {onCreated} {onView}
        editor={AuctionEditor}
        bind:showNewButton={showNewButton}
        bind:entities={auctions}
    />
{/if}