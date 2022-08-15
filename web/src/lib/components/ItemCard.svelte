<script lang="ts">
    import { onMount } from "svelte";
    import { putStart, getItem, deleteEntity, ErrorHandler, type ILoader } from "$lib/services/api";
    import { token, user, Info } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction } from "$lib/types/auction";
    import { Listing } from "$lib/types/listing";
    import type { Item } from "$lib/types/item";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import Avatar from "$lib/components/Avatar.svelte";
    import Confirmation from "$lib/components/Confirmation.svelte";
    import Countdown from "$lib/components/Countdown.svelte";
    import DateFormatter from "$lib/components/DateFormatter.svelte";

    export let entity: IEntity;
    $: item = <Item>(<unknown>entity);

    $: topBid = (item instanceof Auction) ? item.topBid() : null;

    let itemTweeted;
    let itemViewed;
    let starting = false;

    let confirmation: any = null;

    export let onEdit = (_: Item) => {};
    export let onView = (_: Item) => {};
    export let onDelete = () => {};

    function view() {
        if (item.started) {
            var viewedItems = (localStorage.getItem(`${item.endpoint}-viewed`) || "").split(",");
            viewedItems.push(item.key);
            viewedItems = viewedItems.filter((v, i, s) => s.indexOf(v) === i).filter(e => e !== "");
            localStorage.setItem(`${item.endpoint}-viewed`, viewedItems.join(","));
            itemViewed = true;
            onView(item);
        }

        window.open(getUrl(), "_blank");
    }

    function getUrl() {
        return `${window.location.protocol}//${window.location.host}/${item.endpoint}/${item.key}`;
    }

    function openTwitter() {
        var tweetedItems = (localStorage.getItem(`${item.endpoint}-tweeted`) || "").split(",");
        tweetedItems.push(item.key);
        tweetedItems = tweetedItems.filter((v, i, s) => s.indexOf(v) === i).filter(e => e !== "");
        localStorage.setItem(`${item.endpoint}-tweeted`, tweetedItems.join(","));
        itemTweeted = true;
        let url = encodeURIComponent(getUrl());
        let text = encodeURIComponent(`I am selling for sats: ${item.title}`);
        let specs = window.screen.availWidth >= 1024 ? "width=500,height=500" : undefined;
        window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', specs);
    }

    function start() {
        starting = true;
        Info.set("Checking your Twitter account...");
        putStart($token, item.endpoint, item.key,
            () => {
                getItem(item.loader, $token, item.key,
                    a => {
                        entity = a;
                        user.update(u => { if (u) { u.twitter.usernameVerified = true; } return u; });
                        starting = false;
                        if (item instanceof Auction) {
                            Info.set("Your auction is now running...");
                        } else if (item instanceof Listing) {
                            Info.set("Your listing is now active...");
                        }
                    },
                    new ErrorHandler(false, () => starting = false));
                },
            new ErrorHandler(true, () => starting = false));
    }

    function del() {
        confirmation = {
            onContinue: () => {
                deleteEntity($token, entity, onDelete);
            }
        };
    }

    onMount(async () => {
        confirmation = null;
        itemTweeted = item.key.length !== 0 && (localStorage.getItem(`${item.endpoint}-tweeted`) || "").includes(item.key);
        itemViewed = item.key.length !== 0 && (localStorage.getItem(`${item.endpoint}-viewed`) || "").includes(item.key);
    });
</script>

<div class="glowbox">
<div class="card md:card-side bg-base-300 max-w-full overflow-hidden shadow-xl my-3">
    <figure class="md:h-auto flex justify-center">
        {#each item.media as photo, i}
            {#if i === 0}
                <img class="object-contain" src={photo.url} alt="Item" />
            {/if}
        {/each}
    </figure>
    <div class="card-body">
        <h2 class="card-title mb-2">
            {item.title}
        </h2>
        {#if item.started && !item.ended}
            <div class="badge badge-primary">running</div>
        {:else if item.ended}
            <div class="badge badge-primary">ended</div>
        {/if}
        {#if item instanceof Auction}
            <div class="badge badge-secondary">auction</div>
        {:else if item instanceof Listing}
            <div class="badge badge-secondary">fixed price</div>
        {/if}
        {#if item.started && !item.ended}
            <div class="float-root">
                <div class="py-5 float-left">
                    <div class="lg:flex">
                        <div class="mt-4 lg:mt-0">
                            <div class="ml-4 mt-2">
                                {#if item instanceof Auction}
                                    <Countdown untilDate={item.end_date} />
                                {:else}
                                    <nobr class="text-2xl">Your listing is live!</nobr>
                                {/if}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
        {#if !item.ended && !itemViewed}
        <div class="mt-2">
            <p class="text-center">
                {#if !itemTweeted && !item.started}
                Create your tweet and don't forget to attach some pictures
                {:else if itemTweeted && !item.started}
                Start your sale
                {:else if item.started}
                View your listing
                {/if}
            </p>
            <div class="pt-5 mb-5 w-full flex items-center justify-center rounded">
                <ul class:lg:steps-horizontal={!item.started} class="steps steps-vertical">
                    <li class="step" class:step-primary={true} class:lg:mb-5={!item.started} class:lg:ml-5={!item.started}>
                        {#if !itemTweeted && !item.started}
                            <div class="glowbutton glowbutton-tweet ml-2 mr-5 my-5" class:lg:mr-0={!item.started} class:lg:my-0={!item.started} on:click|preventDefault={openTwitter}></div>
                        {:else}
                            <button class="btn mx-2" on:click={openTwitter}>Tweet</button>
                        {/if}
                    </li>
                    <li class="step" class:lg:mb-5={!item.started} class:step-primary={itemTweeted || item.started}>
                        {#if itemTweeted && !item.started && !starting}
                            <div class="glowbutton glowbutton-start ml-2 mr-5" class:lg:mr-0={!item.started} on:click|preventDefault={start}></div>
                        {:else}
                            <button class="btn btn-disabled mx-2">Start</button>
                        {/if}
                    </li>
                    <li class="step" class:lg:mb-5={!item.started} class:lg:mr-5={!item.started} class:step-primary={item.started}>
                        {#if item.started}
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
            {#if item.start_date && item.end_date && !item.started}
                From:
                <DateFormatter date={item.start_date} />
                <br />
                To:
                <DateFormatter date={item.end_date} />
            {/if}
            {#if item instanceof Auction}
                {#if item.has_winner}
                    <br />
                    <span>Winner: @{item.winner_twitter_username}</span>
                    <br />
                    <span>Amount: <AmountFormatter satsAmount={item.topAmount()} /></span>
                {:else if !item.started}
                    <br />
                    <span>{item.duration_str} /</span>
                    <span>Start: <AmountFormatter satsAmount={item.starting_bid} /> /</span>
                    <span>Reserve: <AmountFormatter satsAmount={item.reserve_bid} /></span>
                {:else}
                    {#if topBid && topBid.buyer}
                        <br />
                        Top bid: <AmountFormatter satsAmount={topBid.amount} /> by <Avatar account={topBid.buyer} />
                    {/if}
                    <br />
                    <span>Bids: {item.bids.length}</span>
                {/if}
            {:else if item instanceof Listing}
                <br />
                <span>Price: ~<AmountFormatter usdAmount={item.price_usd} /></span>
                <br />
                <span>Avalable quantity: {item.available_quantity}</span>
            {/if}
        </p>
        <div class="mt-2 card-actions justify-end">
            {#if confirmation}
                <Confirmation onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
            {:else}
                {#if item instanceof Listing || !item.started}
                    <button class="btn mx-1" on:click={() => onEdit(item)}>Edit</button>
                    <button class="btn mx-1" on:click={del}>Delete</button>
                {:else if itemViewed || item.ended}
                    <button class="btn mx-1" on:click={view}>View</button>
                {/if}
            {/if}
        </div>
    </div>
</div>
</div>