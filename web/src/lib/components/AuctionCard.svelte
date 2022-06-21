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

    export let onEdit = (_: Auction) => {};
    export let onView = (_: Auction) => {};
    export let onDelete = () => {};

    function view() {
        if (auction.started) {
            var viewedAuctions = (localStorage.getItem('auctions-viewed') || "").split(",");
            viewedAuctions.push(auction.key);
            viewedAuctions = viewedAuctions.filter((v, i, s) => s.indexOf(v) === i).filter(e => e !== "");
            localStorage.setItem('auctions-viewed', viewedAuctions.join(","));
            auctionViewed = true;
            onView(auction);
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
        let specs = window.screen.availWidth >= 1024 ? "width=500,height=500" : undefined;
        window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', specs);
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

<div class="glowbox">
<div class="card md:card-side bg-base-300 max-w-full overflow-hidden shadow-xl my-3">
    <figure class="md:h-auto flex justify-center">
        {#each auction.media as photo, i}
            {#if i === 0}
                <img class="object-contain" src={photo.url} alt="Auctioned object" />
            {/if}
        {/each}
    </figure>
    <div class="card-body">
        <h2 class="card-title mb-2">
            {auction.title}
            {#if auction.started && !auction.ended}
                <div class="badge badge-primary">running</div>
            {:else if auction.ended}
                <div class="badge badge-secondary">ended</div>
            {/if}
        </h2>
        {#if auction.started && !auction.ended}
            <div class="float-root">
                <div class="py-5 float-left">
                    <div class="lg:flex">
                        <div class="mt-4 lg:mt-0">
                            <div class="ml-4 mt-2">
                                <Countdown untilDate={auction.end_date} />
                            </div>
                        </div>
                    </div>
                </div>
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
                <ul class:lg:steps-horizontal={!auction.started} class="steps steps-vertical">
                    <li class="step" class:step-primary={true} class:lg:mb-5={!auction.started} class:lg:ml-5={!auction.started}>
                        {#if !auctionTweeted && !auction.started}
                            <div class="glowbutton glowbutton-tweet ml-2 mr-5 my-5" class:lg:mr-0={!auction.started} class:lg:my-0={!auction.started} on:click|preventDefault={openTwitter}></div>
                        {:else}
                            <button class="btn mx-2" on:click={openTwitter}>Tweet</button>
                        {/if}
                    </li>
                    <li class="step" class:lg:mb-5={!auction.started} class:step-primary={auctionTweeted || auction.started}>
                        {#if auctionTweeted && !auction.started && !starting}
                            <div class="glowbutton glowbutton-start ml-2 mr-5" class:lg:mr-0={!auction.started} on:click|preventDefault={start}></div>
                        {:else}
                            <button class="btn btn-disabled mx-2">Start</button>
                        {/if}
                    </li>
                    <li class="step" class:lg:mb-5={!auction.started} class:lg:mr-5={!auction.started} class:step-primary={auction.started}>
                        {#if auction.started}
                            <div class="glowbutton glowbutton-view ml-2 mr-5 mb-5" on:click|preventDefault={view}></div>
                        {:else}
                            <button class="btn mx-2" on:click={view}>View</button>
                        {/if}
                    </li>
                </ul>
            </div>
        </div>
        {/if}
        <p class="whitespace-nowrap">
            {#if auction.start_date && auction.end_date}
                From:
                <DateFormatter date={auction.start_date} />
                <br />
                To:
                <DateFormatter date={auction.end_date} />
            {/if}
            <br />
            {#if !auction.started}
                <span>{auction.duration_str} /</span>
            {/if}
            <span>Start: {auction.starting_bid} /</span>
            <span>Reserve: {auction.reserve_bid}</span>
            {#if auction.started}
                <span class="lg:float-right">Bids: {auction.bids.length}</span>
            {/if}
        </p>
        <div class="mt-2 card-actions justify-end">
            {#if confirmation}
                    <Confirmation onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
            {:else}
                {#if !auction.started}
                        <button class="btn mx-1" on:click={() => onEdit(auction)}>Edit</button>
                        <button class="btn mx-1" on:click={del}>Delete</button>
                {:else if auctionViewed || auction.ended}
                        <button class="btn mx-1" on:click={view}>View</button>
                {/if}
            {/if}
        </div>
    </div>
</div>
</div>