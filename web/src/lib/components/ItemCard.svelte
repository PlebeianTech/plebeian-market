<script lang="ts">
    import { onMount } from "svelte";
    import { putStartTwitter, getItem, deleteEntity, ErrorHandler } from "$lib/services/api";
    import { token, user, Info } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction } from "$lib/types/auction";
    import { Listing } from "$lib/types/listing";
    import { Category, type Item } from "$lib/types/item";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import Confirmation from "$lib/components/Confirmation.svelte";
    import DateFormatter from "$lib/components/DateFormatter.svelte";

    // svelte-ignore unused-export-let
    export let isEditable = false;
    // svelte-ignore unused-export-let
    export let showCampaign = false;
    // svelte-ignore unused-export-let
    export let showOwner = false;

    export let entity: IEntity;
    $: item = <Item>(<unknown>entity);
    $: url = item ? `${window.location.protocol}//${window.location.host}/${item.endpoint}/${item.key}` : "";

    let itemTweeted;

    let box; // the whole box representing this item (the HTML Element)
    let confirmation: any = null;

    export let onEdit = (_: Item) => {};
    export let onEntityChanged = () => {};

    function openTwitter() {
        var tweetedItems = (localStorage.getItem(`${item.endpoint}-tweeted`) || "").split(",");
        tweetedItems.push(item.key);
        tweetedItems = tweetedItems.filter((v, i, s) => s.indexOf(v) === i).filter(e => e !== "");
        localStorage.setItem(`${item.endpoint}-tweeted`, tweetedItems.join(","));
        itemTweeted = true;
        let text = encodeURIComponent(`Selling for sats: ${item.title} #PlebeianMarket`);
        let specs = window.screen.availWidth >= 1024 ? "width=500,height=500" : undefined;
        window.open(`https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${text}`, '_blank', specs);
    }

    let starting = false;
    function start() {
        starting = true;
        Info.set("Checking your Twitter account...");
        putStartTwitter($token, item.endpoint, item.key,
            () => {
                getItem(item.loader, $token, item.key,
                    a => {
                        entity = a;
                        window.location.hash = `#item-${item.key}`;
                        starting = false;
                        if (item instanceof Auction) {
                            user.update(u => { if (u) { u.twitterUsernameVerified = true; u.hasActiveAuctions = true; } return u; });
                            Info.set("Your auction is now active...");
                        } else if (item instanceof Listing) {
                            user.update(u => { if (u) { u.twitterUsernameVerified = true; u.hasActiveListings = true; } return u; });
                            Info.set("Your listing is now active...");
                        }
                        onEntityChanged();
                    },
                    new ErrorHandler(false, () => starting = false));
                },
            new ErrorHandler(true, () => starting = false));
    }

    function del() {
        confirmation = {
            onContinue: () => {
                deleteEntity($token, entity, onEntityChanged);
            }
        };
    }

    onMount(async () => {
        confirmation = null;
        itemTweeted = item.key.length !== 0 && (localStorage.getItem(`${item.endpoint}-tweeted`) || "").includes(item.key);

        if (item && window.location.hash === `#item-${item.key}`) {
            window.scrollTo(0, box.offsetTop);
        }
    });
</script>

<div bind:this={box} class="glowbox">
    <div class="card md:card-side bg-base-300 max-w-full overflow-hidden shadow-xl my-3">
        <div class="card-body">
            <h2 class="card-title mb-2">
                {item.title}
            </h2>
            <div class="mt-2">
                <p class="text-center">
                    {#if !itemTweeted}
                        {#if item.category !== Category.Time}
                            Create your tweet and don't forget to attach four pictures!
                            <br />
                            (with the best one first)
                        {:else}
                            Create a tweet!
                        {/if}
                    {:else}
                        Start your sale
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
                            <a class="btn mx-2" href={url}>View</a>
                        </li>
                    </ul>
                </div>
            </div>
            <p class="whitespace-nowrap">
                {#if item.start_date && item.end_date}
                    <br />
                    From: <DateFormatter date={item.start_date} />
                    <br />
                    To: <DateFormatter date={item.end_date} />
                {/if}
                {#if item instanceof Auction}
                    <br />
                    <span>{item.duration_str}</span>
                    <br />
                    <span>Start: <AmountFormatter satsAmount={item.starting_bid} /> /</span>
                    <span>Reserve: <AmountFormatter satsAmount={item.reserve_bid} /></span>
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
                    <button class="btn mx-1" on:click={() => onEdit(item)}>Edit</button>
                    <button class="btn mx-1" on:click={del}>Delete</button>
                {/if}
            </div>
        </div>
    </div>
</div>