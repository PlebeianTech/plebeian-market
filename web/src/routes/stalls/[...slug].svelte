<svelte:head>
    <title>Market Stall</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { stallName: slug } }
    }
</script>

<script lang="ts">
    import { token, user, Info } from "$lib/stores";
    import { Auction, fromJson } from "$lib/types/auction";
    import StallView from "$lib/components/StallView.svelte";
    import ListView from "$lib/components/ListView.svelte";
    import AuctionCard from "$lib/components/AuctionCard.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import { getProfile } from "$lib/services/api";
    import { onMount } from "svelte";
    import { afterNavigate } from '$app/navigation';

    export let stallName: string;
    let auctions: Auction[] | null = [];
    let userOwnsStall = false;
    let viewedAuctions = (localStorage.getItem('auctions-viewed') || "").split(",");

    // NB: the "new" button is shown when there are no auctions that are not ended and not viewed
    // (basically auctions that have been just created and the user didn't go through the whole tweet-start-view flow, *unless* they already ended)
    $: showNewButton = auctions === null || !auctions.find(a => !a.ended && viewedAuctions.indexOf(a.key) === -1);

    function fetchProfile(tokenValue) {
        getProfile(tokenValue,
            u => {
                user.set(u);
                if ($user && $user.nym === stallName) {
                    userOwnsStall = true;
                }
            });
    }

    function onCreated() {
        user.update((u) => { u!.hasAuctions = true; return u; });
        Info.set("Your auction will start when we verify your tweet!");
    }

    function onView(auction) {
        // NB: using assignement rather than .push() to trigger recalculation of showNewButton
        viewedAuctions = [...viewedAuctions, auction.key];
    }


    afterNavigate(() => {
        fetchProfile($token);
    });

    onMount(async () => {
        fetchProfile($token);
    });

</script>


{#if userOwnsStall}
    <ListView
        title="My Auctions"
        loader={{endpoint: 'auctions', fromJson}} newEntity={() => new Auction()}
        card={AuctionCard} editor={AuctionEditor} bind:showNewButton={showNewButton}
        {onCreated} {onView}
        bind:entities={auctions}>
    </ListView>
{:else}
    <StallView
        loader={{endpoint: `users/${stallName}/auctions`, fromJson}}
        stallName={stallName}
        bind:entities={auctions}
    />
{/if}