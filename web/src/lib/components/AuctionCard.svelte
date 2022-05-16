<script lang="ts">
    import { onMount } from "svelte";
    import { fetchAPI } from "../services/api";
    import { type Auction, fromJson } from "../types/auction";
    import { token, user, Error } from "../stores";
    import Confirmation from "./Confirmation.svelte";
    import Countdown from "./Countdown.svelte";
    import DateFormatter from "./DateFormatter.svelte";

    export let auction : Auction;
    let twitterOpened = false;
    let auctionViewed = auction.key.length !== 0 && (localStorage.getItem('auctions-viewed') || "").includes(auction.key);

    let confirmation: any = null;

    export let onEdit = (auction) => {};

    export let onDelete = () => {};

    function view() {
        if (auction.started) {
            var viewedAuctions = (localStorage.getItem('auctions-viewed') || "").split(",");
            viewedAuctions.push(auction.key);
            viewedAuctions = viewedAuctions.filter((v, i, s) => s.indexOf(v) === i).filter(e => e !== "");
            localStorage.setItem('auctions-viewed', viewedAuctions.join(","));
            auctionViewed = true;
        }

        window.open(getUrl(), "_blank");
    }

    function getUrl() {
        return `${window.location.protocol}//${window.location.host}/auctions/${auction.key}`;
    }

    function openTwitter() {
        twitterOpened = true;
        let url = encodeURIComponent(getUrl());
        let text = encodeURIComponent(`I am auctioning for sats: ${auction.title}`);
        window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank');
    }

    function start() {
        fetchAPI(`/auctions/${auction.key}/start-twitter`, 'PUT', $token, null,
            (response) => {
                if (response.status === 200) {
                    fetchAPI(`/auctions/${auction.key}`, 'GET', $token, null,
                        (auctionResponse) => {
                            if (auctionResponse.status === 200) {
                                auctionResponse.json().then(data => {
                                    auction = fromJson(data.auction);
                                    user.update((u) => {
                                        if (u) {
                                            u.twitterUsernameVerified = true;
                                        }
                                        return u;
                                    });
                                });
                            }
                        }
                    );
                }  else {
                    response.json().then(data => {
                        Error.set(data.message);
                    });
                }
            }
        );
    }

    function deleteAuction() {
        confirmation = {
            onContinue: () => {
                fetchAPI(`/auctions/${auction.key}`, 'DELETE', $token, null,
                    (response) => {
                        if (response.status === 200) {
                            onDelete();
                        }
                    });
                }
        };
    }

    onMount(async () => { confirmation = null; });
</script>

<div class="card bg-base-100 max-w-full p-4 rounded overflow-hidden shadow-lg my-3">
    <div class="text-center">
        <h3 class="text-2xl">{auction.title}</h3>
        <span class=" font-mono">
            {#if auction.started && !auction.ended}
                (running)
            {:else if auction.ended}
                (ended)
            {/if}
        </span>
    </div>
    <p class="mt-2">Duration: {auction.duration_str} {#if auction.start_date && auction.end_date}/ <DateFormatter date={auction.start_date} /> - <DateFormatter date={auction.end_date} />{/if}</p>
    <p><span>Starting bid: {auction.starting_bid}</span> <span>Reserve bid: {auction.reserve_bid}</span><span class="float-right">Bids: {auction.bids.length}</span></p>
    {#each auction.media as photo, i}
        {#if i === 0}
            <div id="{photo.twitter_media_key}" class="w-24 rounded">
                <img src={photo.url} class="rounded" alt="Auctioned object" />
            </div>
        {/if}
    {/each}
    {#if confirmation}
        <div class="mt-2 py-5">
            <Confirmation onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
        </div>
    {:else}
        <div class="mt-2 float-root">
            <div class="py-5 float-left">
                {#if auction.started && !auction.ended}
                    <Countdown untilDate={auction.end_date} />
                {/if}
            </div>
            {#if !auction.started}
            <div class="py-5 float-right">
                    <button class="btn mx-1" on:click={() => onEdit(auction)}>Edit</button>
                    <button class="btn mx-1" on:click={deleteAuction}>Delete</button>
            </div>
            {:else if auctionViewed}
            <div class="py-5 float-right">
                <button class="btn mx-1" on:click={view}>View</button>
            </div>
            {/if}
        </div>
    {/if}
    {#if !auction.ended && !auctionViewed}
    <div class="mt-2">
        <p class="text-center">
            {#if !twitterOpened && !auction.started}
            Create your tweet and don't forget to attach some pictures
            {:else if twitterOpened && !auction.started}
            Start your auction
            {:else if auction.started}
            View your auction
            {/if}
        </p>
        <div class="py-5 w-full flex items-center justify-center rounded">
            <ul class="steps steps-vertical lg:steps-horizontal">
                <li class="step" class:step-primary={twitterOpened || auction.started}>
                    {#if !twitterOpened && !auction.started}
                        <div class="glowbutton glowbutton-tweet mx-2" on:click|preventDefault={openTwitter}></div>
                    {:else}
                        <button class="btn btn-disabled mx-2" on:click={openTwitter}>Tweet</button>
                    {/if}
                </li>
                <li class="step" class:step-primary={auction.started}>
                    {#if twitterOpened && !auction.started}
                        <div class="glowbutton glowbutton-start mx-2" on:click|preventDefault={start}></div>
                    {:else}
                        <button class="btn btn-disabled mx-2">Start</button>
                    {/if}
                </li>
                <li class="step" class:step-primary={auction.started}>
                    {#if auction.started}
                        <div class="glowbutton glowbutton-view ml-2" on:click|preventDefault={view}></div>
                    {:else}
                        <button class="btn mx-2" on:click={view}>View</button>
                    {/if}
                </li>
            </ul>
        </div>
    </div>
    {/if}
</div>