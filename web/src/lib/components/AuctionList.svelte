<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { getAuctions, putAuction, postAuction } from "../services/api";
    import { Auction } from "../types/auction";
    import { token, user, Info } from "../stores";
    import AuctionCard from "./AuctionCard.svelte";
    import AuctionEditor from "./AuctionEditor.svelte";
    import Loading from "./Loading.svelte";

    let currentAuction: Auction | undefined;
    let auctions: Auction[] | null = null;

    let viewedAuctions = (localStorage.getItem('auctions-viewed') || "").split(",");

    // NB: the "new" button is shown when there are no auctions that are not ended and not viewed
    // (basically auctions that have been just created and the user didn't go through the whole tweet-start-view flow, *unless* they already ended)
    $: showNewButton = auctions === null || !auctions.find(a => !a.ended && viewedAuctions.indexOf(a.key) === -1);

    function fetchAuctions(successCB: () => void = () => {}) {
        getAuctions($token,
            a => {
                auctions = a;
                successCB();
            });
    }

    function saveCurrentAuction() {
        if (!currentAuction) {
            return;
        }
        currentAuction.invalidTitle = currentAuction.title.length === 0;
        currentAuction.invalidDescription = currentAuction.description.length === 0;
        if (currentAuction.invalidTitle || currentAuction.invalidDescription) {
            return;
        }

        auctions = null;

        if (currentAuction.key !== "") {
            putAuction($token, currentAuction,
                () => {
                    fetchAuctions(() => { currentAuction = undefined; })
                });
        } else {
            postAuction($token, currentAuction,
                () => {
                    user.update((u) => { u!.hasAuctions = true; return u; });
                    Info.set("Your auction will start when we verify your tweet!");
                    fetchAuctions(() => { currentAuction = undefined; });
                });
        }
    }

    function onDelete() {
        auctions = null;
        fetchAuctions();
    }

    function onView(auction) {
        // NB: using assignement rather than .push() to trigger recalculation of showNewButton
        viewedAuctions = [...viewedAuctions, auction.key];
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    onMount(async () => {
        fetchAuctions(() => { currentAuction = auctions && auctions.length === 0 ? new Auction() : undefined; });
        interval = setInterval(fetchAuctions, 10000);
    });

    onDestroy(() => {
        if (interval) {
            clearInterval(interval);
            interval = undefined;
        }
    });
</script>

<svelte:head>
    <title>My Auctions</title>
</svelte:head>

<div class="pt-10 flex justify-center items-center">
    <section class="w-11/12 md:w-auto mx-20">
        {#if currentAuction}
            <AuctionEditor bind:auction={currentAuction} onSave={saveCurrentAuction} onCancel={() => currentAuction = undefined} />
        {:else if auctions === null}
            <Loading />
        {:else}
            {#if showNewButton}
                <div class="flex items-center justify-center mb-4">
                    <div class="glowbutton glowbutton-new" on:click|preventDefault={() => currentAuction = new Auction()}></div>
                </div>
            {/if}
            {#each auctions as auction}
                <AuctionCard auction={auction} onEdit={(a) => currentAuction = a} onView={onView} onDelete={onDelete} />
            {/each}
        {/if}
    </section>
</div>
