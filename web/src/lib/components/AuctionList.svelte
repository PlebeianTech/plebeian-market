<script lang="ts">
    import {onDestroy, onMount} from 'svelte';
    import {getAuctions, putAuction, postAuction} from "../services/api";
    import type {Auction} from "../types/auction";
    import {token, user, Info} from "../stores";
    import AuctionCard from "./AuctionCard.svelte";
    import AuctionEditor from "./AuctionEditor.svelte";
    import Loading from "./Loading.svelte";
    import TimeAuctionEditor from "./TimeAuctionEditor.svelte";

    function emptyAuction() {
        return {
            key: "",
            title: "",
            description: "",
            started: false,
            ended: false,
            starting_bid: 0,
            reserve_bid: 0,
            reserve_bid_reached: false,
            shipping_from: "",
            duration_hours: 24,
            end_date_extended: false,
            bids: [],
            media: [],
            is_mine: true,
            is_physical: true,
        };
    }

    function emptyTimeAuction() {
        return {
            key: "",
            title: "",
            description: "",
            started: false,
            ended: false,
            starting_bid: 0,
            reserve_bid: 0,
            reserve_bid_reached: false,
            shipping_from: "",
            duration_hours: 24,
            end_date_extended: false,
            bids: [],
            media: [],
            is_mine: true,
        };
    }

    let currentAuction: Auction | undefined;
    let auctions: Auction[] | null = null;

    function fetchAuctions(successCB: () => void = () => {
    }) {
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
                    fetchAuctions(() => {
                        currentAuction = undefined;
                    })
                });
        } else {
            postAuction($token, currentAuction,
                () => {
                    user.update((u) => {
                        u!.hasAuctions = true;
                        return u;
                    });
                    Info.set("Your auction will start when we verify your tweet!");
                    fetchAuctions(() => {
                        currentAuction = undefined;
                    });
                });
        }
    }

    function onDelete() {
        auctions = null;
        fetchAuctions();
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    onMount(async () => {
        fetchAuctions(() => {
            currentAuction = auctions && auctions.length === 0 ? emptyAuction() : undefined;
        });
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
    <section class="w-11/12 lg:w-3/5">
        {#if currentAuction}
            {#if currentAuction.is_physical}
            <AuctionEditor bind:auction={currentAuction} onSave={saveCurrentAuction} onCancel={() => currentAuction = undefined} />
            {:else}
            <TimeAuctionEditor bind:auction={currentAuction} onSave={saveCurrentAuction} onCancel={() => currentAuction = undefined} />
            {/if}
        {:else if auctions == null}
            <Loading />
        {:else}
            <div class="flex justify-center my-2 text-xl"><p>What are you selling?</p></div>
            <div class="flex items-center justify-center mb-4">
                <div class="w-1/4">
                <div class="glowbutton glowbutton-physical" on:click|preventDefault={() => currentAuction = emptyAuction()}></div>
                </div>
                <div class="w-1/4">
                <div class="glowbutton glowbutton-time" on:click|preventDefault={() => currentAuction = emptyTimeAuction()}></div>
                </div>
            </div>
            {#each auctions as auction, i}
                <AuctionCard auction={auction} onEdit={(auction) => currentAuction = auction} onDelete={onDelete} />
            {/each}
        {/if}
    </section>
</div>