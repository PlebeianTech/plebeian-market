<script lang="ts">
    import { onMount } from "svelte";
    import type { Auction } from "../types/auction";
    import Countdown from "./Countdown.svelte";
    import DateFormatter from "./DateFormatter.svelte";
    export let auction : Auction;
    let confirmation: any = null;
    export let onView = (_: Auction) => {};

    function view() {
        if (auction.started) {
            var viewedAuctions = (localStorage.getItem('auctions-viewed') || "").split(",");
            viewedAuctions.push(auction.key);
            viewedAuctions = viewedAuctions.filter((v, i, s) => s.indexOf(v) === i).filter(e => e !== "");
            localStorage.setItem('auctions-viewed', viewedAuctions.join(","));
            onView(auction);
        }

        window.open(getUrl(), "_blank");
    }

    function getUrl() {
        return `${window.location.protocol}//${window.location.host}/auctions/${auction.key}`;
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
        {#if !auction.ended}
        <div class="mt-2">

            <div class="pt-5 mb-5 w-full flex items-center justify-center rounded">
                <ul class:lg:steps-horizontal={!auction.started} class="steps steps-vertical">
                    <li class="step" class:lg:mb-5={!auction.started} class:lg:mr-5={!auction.started} class:step-primary={auction.started}>
                            <div class="glowbutton glowbutton-view ml-2 mr-5 mb-5" on:click|preventDefault={view}></div>
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
            {#if auction.started}
                <span class="lg:float-right">Bids: {auction.bids.length}</span>
            {/if}
        </p>

    </div>
</div>
</div>