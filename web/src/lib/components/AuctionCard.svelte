<script lang="ts">
    import { onMount } from "svelte";
    import { startAuction, getAuction, deleteAuction } from "../services/api";
    import type { Auction } from "../types/auction";
    import { token, user, Info } from "../stores";
    import Confirmation from "./Confirmation.svelte";
    import Countdown from "./Countdown.svelte";
    import DateFormatter from "./DateFormatter.svelte";

    export let auction : Auction;
    let auctionTweeted = auction.key.length !== 0 && (localStorage.getItem('auctions-tweeted') || "").includes(auction.key);
    let auctionViewed = auction.key.length !== 0 && (localStorage.getItem('auctions-viewed') || "").includes(auction.key);
    let starting = false;

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
        var tweetedAuctions = (localStorage.getItem('auctions-tweeted') || "").split(",");
        tweetedAuctions.push(auction.key);
        tweetedAuctions = tweetedAuctions.filter((v, i, s) => s.indexOf(v) === i).filter(e => e !== "");
        localStorage.setItem('auctions-tweeted', tweetedAuctions.join(","));
        auctionTweeted = true;
        let url = encodeURIComponent(getUrl());
        let text = encodeURIComponent(`I am auctioning for sats: ${auction.title}`);
        window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', "width=500,height=500");
    }

    function start() {
        starting = true;
        Info.set("Checking your Twitter account...");
        startAuction($token, auction.key,
            () => {
                getAuction($token, auction.key,
                    a => {
                        auction = a;
                        user.update(u => { if (u) { u.twitterUsernameVerified = true; } return u; });
                        starting = false;
                        Info.set("Your auction is now running...");
                    },
                    () => {
                        starting = false;
                    });
                },
            () => {
                starting = false;
            });
    }

    function del() {
        confirmation = {
            onContinue: () => {
                deleteAuction($token, auction.key, onDelete);
            }
        };
    }

    onMount(async () => { confirmation = null; });
</script>

<div class="card bg-base-300 max-w-full p-4 rounded overflow-hidden shadow-lg my-3">
    <div class="text-center">
        <h3 class="text-4xl">{auction.title}</h3>
        <span class=" font-mono">
            {#if auction.started && !auction.ended}
                (running)
            {:else if auction.ended}
                (ended)
            {/if}
        </span>
    </div>
    {#if auction.start_date && auction.end_date}
    <div class="lg:flex lg:mt-2 text-xl">
        <div>
            <span class="visible lg:invisible lg:w-0 inline-block">From:</span>
            <DateFormatter date={auction.start_date} />
        </div>
        <div class="invisible h-0 lg:h-auto lg:visible">&nbsp;-&nbsp;</div>
        <div>
            <span class="visible lg:invisible lg:w-0 inline-block">To:</span>
            <DateFormatter date={auction.end_date} />
        </div>
    </div>
    {/if}
    <div class="mt-2 text-2xl">
        <div>
            {#if !auction.started}
                <span>{auction.duration_str} /</span>
            {/if}
            <span>Starts at: {auction.starting_bid} /</span>
            <span>Reserve: {auction.reserve_bid}</span>
            {#if auction.started}
                <div class="lg:float-right">Bids: {auction.bids.length}</div>
            {/if}
        </div>
    </div>
    {#if confirmation}
        <div class="mt-2 py-2 lg:py-5">
            <Confirmation onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
        </div>
    {:else}
        <div class="mt-2 float-root">
            <div class="py-5 float-left">
                <div class="lg:flex">
                    <div>
                        {#each auction.media as photo, i}
                            {#if i === 0}
                                <div id="{photo.twitter_media_key}" class="w-36 rounded">
                                    <img src={photo.url} class="rounded" alt="Auctioned object" />
                                </div>
                            {/if}
                        {/each}
                    </div>
                    <div class="mt-4 lg:mt-0">
                        {#if auction.started && !auction.ended}
                            <div class="ml-4 mt-2">
                                <Countdown untilDate={auction.end_date} />
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
            {#if !auction.started}
                <div class="mt-7 lg:mt-0 py-5 float-right">
                    <button class="btn mx-1" on:click={() => onEdit(auction)}>Edit</button>
                    <button class="btn mx-1" on:click={del}>Delete</button>
                </div>
            {:else if auctionViewed || auction.ended}
                <div class="py-5 float-right">
                    <button class="btn mx-1" on:click={view}>View</button>
                </div>
            {/if}
        </div>
    {/if}
    {#if !auction.ended && !auctionViewed}
    <div class="mt-2">
        <p class="text-center">
            {#if !auctionTweeted && !auction.started}
            Create your tweet and don't forget to attach some pictures
            {:else if auctionTweeted && !auction.started}
            Start your auction
            {:else if auction.started}
            View your auction
            {/if}
        </p>
        <div class="pt-5 mb-5 w-full flex items-center justify-center rounded">
            <ul class="steps steps-vertical lg:steps-horizontal">
                <li class="step lg:mb-5 lg:ml-5" class:step-primary={true}>
                    {#if !auctionTweeted && !auction.started}
                        <div class="glowbutton glowbutton-tweet mx-2" on:click|preventDefault={openTwitter}></div>
                    {:else}
                        <button class="btn mx-2" on:click={openTwitter}>Tweet</button>
                    {/if}
                </li>
                <li class="step lg:mb-5" class:step-primary={auctionTweeted || auction.started}>
                    {#if auctionTweeted && !auction.started && !starting}
                        <div class="glowbutton glowbutton-start mx-2" on:click|preventDefault={start}></div>
                    {:else}
                        <button class="btn btn-disabled mx-2">Start</button>
                    {/if}
                </li>
                <li class="step lg:mb-5 lg:mr-5" class:step-primary={auction.started}>
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