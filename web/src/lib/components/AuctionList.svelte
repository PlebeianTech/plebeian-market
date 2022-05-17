<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchAPI } from "../services/api";
    import { type Auction, fromJson } from "../types/auction";
    import { token, user, Info, Error } from "../stores";
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

    function asJson() {
        var json = {};
        for (var k in currentAuction) {
            if (k !== "key" && k !== "bids" && k !== "media" && k !== "start_date" && k !== "end_date") {
                json[k] = currentAuction[k];
            }
        }
        return JSON.stringify(json);
    }

    function handleError(r) {
        r.json().then(data => Error.set(data.message));
    }

    function fetchAuctions() {
        fetchAPI("/auctions", 'GET', $token, null, r => {
            if (r.status === 200) {
                currentAuction = undefined;
                r.json().then(data => {
                    auctions = data.auctions.map(fromJson);
                    if (!(auctions!.length)) {
                        currentAuction = emptyAuction();
                    }
                });
            } else {
                handleError(r);
            }
        });
    }

    function saveCurrentAuction() {
        let auction: Auction = currentAuction!;
        auction.invalidTitle = auction.title.length === 0;
        auction.invalidDescription = auction.description.length === 0;
        if (auction.invalidTitle || auction.invalidDescription) {
            return;
        }

        auctions = null;

        if (auction.key !== "") {
            fetchAPI(`/auctions/${auction.key}`, 'PUT', $token, asJson(), r => {
                if (r.status === 200) {
                    fetchAuctions();
                } else {
                    handleError(r);
                }
            });
        } else {
            fetchAPI("/auctions", 'POST', $token, asJson(), r => {
                if (r.status === 200) {
                    user.update((u) => { u!.hasAuctions = true; return u; });
                    Info.set("Your auction will start when we verify your tweet!");
                    fetchAuctions();
                } else {
                    handleError(r);
                }
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