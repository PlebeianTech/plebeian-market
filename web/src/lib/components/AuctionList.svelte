<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchAPI } from "../services/api";
    import { type Auction, fromJson } from "../types/auction";
    import { token, user, Info, Error } from "../stores";
    import AuctionCard from "./AuctionCard.svelte";
    import AuctionEditor from "./AuctionEditor.svelte";
    import Confirmation from "./Confirmation.svelte";
    import Loading from "./Loading.svelte";

    function emptyAuction() {
        return {
            key: "",
            title: "",
            description: "",
            starting_bid: 0,
            reserve_bid: 0,
            duration_hours: 24,
            bids: [],
            media: [],
        };
    }

    let confirmation: any = null;
    let currentAuction: Auction | undefined;
    let auctions: Auction[] = [];

    function asJson() {
        var json = {};
        for (var k in currentAuction) {
            if (k !== "key" && k !== "bids" && k !== "media" && k !== "start_date" && k !== "end_date") {
                json[k] = currentAuction[k];
            }
        }
        return JSON.stringify(json);
    }

    function checkResponse(response) {
        if (response.status === 200) {
            confirmation = null;
            currentAuction = undefined;
            response.json().then(data => {
                if (data.auctions) {
                    auctions = data.auctions.map(fromJson);
                    if (!auctions.length) {
                        currentAuction = emptyAuction();
                    }
                } else {
                    fetchAPI("/auctions", 'GET', $token, null, checkResponse);
                }
            });
        } else {
            response.json().then(data => {
                Error.set(data.message);
            });
        }
    }

    function saveCurrentAuction() {
        let auction: Auction = currentAuction!;
        auction.invalidTitle = auction.title.length === 0;
        auction.invalidDescription = auction.description.length === 0;
        if (auction.invalidTitle || auction.invalidDescription) {
            return;
        }

        if (auction.key !== "") {
            fetchAPI(`/auctions/${auction.key}`, 'PUT', $token, asJson(), checkResponse);
        } else {
            fetchAPI("/auctions", 'POST', $token, asJson(), (r) => {
                if (r.status === 200) {
                    user.update((u) => { u!.hasAuctions = true; return u; });
                    Info.set("Your auction will start when we verify your tweet!");
                }
                checkResponse(r);
            });
        }
    }

    function deleteAuction(key) {
        confirmation = {
            message: "Type DELETE MY AUCTION below to continue...",
            expectedInput: "DELETE MY AUCTION",
            onContinue: () => { fetchAPI(`/auctions/${key}`, 'DELETE', $token, null, checkResponse); }
        };
    }

    onMount(async () => { fetchAPI("/auctions", 'GET', $token, null, checkResponse); });
</script>

<div class="pt-10 flex justify-center items-center">
    <section class="w-3/5">
        {#if confirmation}
            <Confirmation message={confirmation.message} expectedInput={confirmation.expectedInput} onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
        {:else if currentAuction}
            <AuctionEditor bind:auction={currentAuction} onSave={saveCurrentAuction} onCancel={() => currentAuction = undefined} />
        {:else if auctions == null}
            <Loading />
        {:else}
            <div class="flex items-center justify-center">
                <div class="glowbutton glowbutton-create" on:click|preventDefault={() => currentAuction = emptyAuction()}></div>
            </div>
            {#each auctions as auction}
                <AuctionCard auction={auction} onEdit={(auction) => currentAuction = auction} onDelete={deleteAuction} />
            {/each}
        {/if}
    </section>
</div>