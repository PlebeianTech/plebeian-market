<script lang="ts">
    import { onMount } from 'svelte';
    import { getAuctions, putAuction, postAuction } from "../services/api";
    import type { Auction } from "../types/auction";
    import { token, user, Info } from "../stores";
    import AuctionCard from "./AuctionCard.svelte";
    import AuctionEditor from "./AuctionEditor.svelte";
    import Loading from "./Loading.svelte";

    function emptyAuction() {
        return {
            key: "",
            title: "",
            description: "",
            starting_bid: 0,
            reserve_bid: 0,
            reserve_bid_reached: false,
            duration_hours: 24,
            end_date_extended: false,
            bids: [],
            media: [],
        };
    }

    let currentAuction: Auction | undefined;
    let auctions: Auction[] | null = null;

    function fetchAuctions() {
        getAuctions($token,
            a => {
                auctions = a;
                currentAuction = auctions && auctions.length ? undefined : emptyAuction();
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
            putAuction($token, currentAuction, fetchAuctions);
        } else {
            postAuction($token, currentAuction,
                () => {
                    user.update((u) => { u!.hasAuctions = true; return u; });
                    Info.set("Your auction will start when we verify your tweet!");
                    fetchAuctions();
                });
        }
    }

    function onDelete() {
        auctions = null;
        fetchAuctions();
    }

    onMount(async () => fetchAuctions());
</script>

<svelte:head>
    <title>My Auctions</title>
</svelte:head>

<div class="pt-10 flex justify-center items-center">
    <section class="w-3/5">
        {#if currentAuction}
            <AuctionEditor bind:auction={currentAuction} onSave={saveCurrentAuction} onCancel={() => currentAuction = undefined} />
        {:else if auctions == null}
            <Loading />
        {:else}
            <div class="flex items-center justify-center">
                <div class="glowbutton glowbutton-new" on:click|preventDefault={() => currentAuction = emptyAuction()}></div>
            </div>
            {#each auctions as auction, i}
                {#if i !== 0}
                    <div class="divider"></div> 
                {/if}
                <AuctionCard auction={auction} onEdit={(auction) => currentAuction = auction} onDelete={onDelete} />
            {/each}
        {/if}
    </section>
</div>