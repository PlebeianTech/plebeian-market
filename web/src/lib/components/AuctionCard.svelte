<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { fetchAPI } from "../services/api";
    import { type Auction, fromJson } from "../types/auction";
    import { token, user, Error } from "../stores";
    import Confirmation from "./Confirmation.svelte";
    import Countdown from "./Countdown.svelte";
    import DateFormatter from "./DateFormatter.svelte";

    export let auction : Auction;
    let twitterLinkCopied = false;
    let twitterOpened = false;

    let confirmation: any = null;

    export let onEdit = (auction) => {};

    export let onDelete = () => {};

    function view() {
        goto(`/auctions/${auction.key}`);
    }

    function getUrl() {
        return `https://plebeian.market/auctions/${auction.key}`;
    }

    function copySnippet() {
        navigator.clipboard.writeText(getUrl()).then(() => { twitterLinkCopied = true; });
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
            <div class="py-5 float-right">
                {#if auction.started}
                    <div class="glowbutton glowbutton-view mx-2" on:click|preventDefault={view}></div>
                {:else}
                    <a class="btn mx-1" href="/auctions/{auction.key}">View</a>
                {/if}
                {#if !auction.started}
                    <button class="btn mx-1" on:click={() => onEdit(auction)}>Edit</button>
                    <button class="btn mx-1" on:click={deleteAuction}>Delete</button>
                {/if}
            </div>
        </div>
    {/if}
    {#if !auction.started}
        <div class="mt-2">
            <div class="py-5 w-full flex items-center justify-center rounded">
                <ul class="steps steps-vertical lg:steps-horizontal">
                    <li class="step" class:step-primary={twitterLinkCopied}>
                        {#if !twitterLinkCopied && !twitterOpened}
                            <div class="glowbutton glowbutton-copy mx-2" on:click|preventDefault={copySnippet}></div>
                        {:else}
                            <button class="btn mx-2" on:click={copySnippet}>Copied!</button>
                        {/if}
                    </li>
                    <li class="step" class:step-primary={twitterOpened}>
                        {#if twitterLinkCopied && !twitterOpened}
                            <div class="glowbutton glowbutton-tweet mx-2" on:click|preventDefault={openTwitter}></div>
                        {:else}
                            <button class="btn mx-2" on:click={openTwitter}>Tweet</button>
                        {/if}
                    </li>
                    <li class="step">
                        {#if twitterLinkCopied && twitterOpened}
                            <div class="glowbutton glowbutton-start ml-2" on:click|preventDefault={start}></div>
                        {:else}
                            <button class="btn mx-2" on:click={start}>Start</button>
                        {/if}
                    </li>
                </ul>
            </div>
        </div>
    {/if}
</div>