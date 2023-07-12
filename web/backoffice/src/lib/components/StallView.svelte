<script lang="ts">
    import { onMount } from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';
    import { goto } from "$app/navigation";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import { putPublish, getFeaturedAvatars, postMedia } from "$lib/services/api";
    import { Info, token, user, AuthRequired } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction, TimeAuction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import type { IAccount, Badge } from "$lib/types/user";
    import { Category } from '$lib/types/item';
    import Faketoshi from "$lib/images/Bitko-Illustration-Faketoshi.svg"
    import ExternalLinks from './externalLinks.svelte';
    import Spaceship from "$lib/images/spaceship.jpg";

    export let baseUrl: string;

    export let owner: IAccount | null;
    export let title: string | null;
    export let description: string | null;

    export let isOwnStall = false;
    export let isCampaignStall = false;
    export let campaignKey: string | null = null;

    export let showItemsCampaign: boolean;
    export let canAddItems: boolean;
    export let showActiveAuctions: boolean = true;
    export let showPastAuctions: boolean = true;
    export let showActiveListings: boolean = true;
    export let showPastListings: boolean = true;

    let availableFilters = ['active', 'past'];
    let auctionFilter = 'active';
    let listingFilter = 'active';

    let auctionsLists: { [key: string]: ListView } = {};
    let listingsLists: { [key: string]: ListView } = {};

    function onAuctionSave(key: string, entity: IEntity) {
        user.update((u) => {
            u!.hasItems = true;
            if (isOwnStall) {
                u!.hasOwnItems = true;
            }
            return u;
        });

        let auction = entity as Auction;

        if (auction.added_media.length !== 0) {
            postMedia($token, auction.endpoint, key, auction.added_media, () => onForceReload());
        }

        if (auction.category === Category.Time) {
            putPublish($token, auction.endpoint, key,
                () => {
                    onForceReload();
                    goto(`/auctions/${key}`);
                });
        } else {
            if (!auction.started) {
                Info.set("Now hit Publish!");
            }
        }
    }

    function onListingSave(key: string, entity: IEntity) {
        user.update((u) => {
            u!.hasItems = true;
            if (isOwnStall) {
                u!.hasOwnItems = true;
            }
            return u;
        });

        let listing = entity as Listing;

        if (listing.added_media.length !== 0) {
            postMedia($token, listing.endpoint, key, listing.added_media, () => onForceReload());
        }

        if (!listing.started) {
            Info.set("Now hit Publish!");
        }
    }

    function onForceReload() {
        if (canAddItems) {
            for (let [_, l] of Object.entries(auctionsLists)) {
                if (l.fetchEntities) {
                    l.fetchEntities();
                }
            }
            for (let [_, l] of Object.entries(listingsLists)) {
                if (l.fetchEntities) {
                    l.fetchEntities();
                }
            }
        }
    }

    function loginAndNewItem(setCurrent: (IEntity) => void, getNewItem: () => IEntity) {
        if ($user && $user.nym) {
            setCurrent(getNewItem());
        } else {
            AuthRequired.set({cb: () => setCurrent(getNewItem())});
        }
    }

    function loginAndScrollIntoView({ target }) {
        if ($user && $user.nym) {
            scrollIntoView(target);
        } else {
            AuthRequired.set({cb: () => scrollIntoView(target)});
        }
    }

    function scrollIntoView(target) {
        const el = document.querySelector(target.getAttribute('href'))
        if (!el) return;
        el.scrollIntoView({
            behavior: 'smooth'
        })
    }

    let featuredAuctionAvatars: {url: string, entity_key: string}[] = [];

    onMount(async () => {
        if (isCampaignStall && campaignKey) {
            getFeaturedAvatars(campaignKey,
            (auctionAvatars, _) => {
                featuredAuctionAvatars = auctionAvatars;
            });
        }
    });
</script>

{#if isCampaignStall}
    <!-- HERO SECTION STATIC CONTENT -->
    <div class="bg-fixed bg-no-repeat bg-cover bg-bottom" style="background-image: url('{Spaceship}')">
        <!-- FILTER -->
        <div class="bg-gradient-to-b from-pink-700/90 to-pink-500/40">
            <!-- HERO -->
            <div class="lg:w-2/3 mx-auto grid lg:grid-cols-2 gap-4">
            <!-- COL -->
            <div class="mt-20 p-4">
                <!-- FULL WIDTH BANNER -->
                <!-- <img src={BannerImg} alt=""> -->
                <h1 class="lg:text-7xl text-4xl font-bold text-white lg:text-left text-center">{title}</h1>

                <!-- BUTTONS -->
                <div class="lg:w-2/3 grid place-items-center">
                <a href="#anchorId" on:click|preventDefault={loginAndScrollIntoView} class="btn btn-primary uppercase font-bold my-8 w-full">Auction 1-hour of your time</a>
                <p class="text-3xl mb-3 font-bold">OR</p>
                <div class="mb-8 w-full grid grid-cols-2 gap-4">
                    <a href="#anchorId" on:click|preventDefault={loginAndScrollIntoView} class="btn btn-outline text-white uppercase font-bold my-4">Auction Item</a>
                    <a href="#anchorIdFixedPrice" on:click|preventDefault={loginAndScrollIntoView} class="btn btn-outline text-white uppercase font-bold my-4">Fixed Price</a>
                </div>
                </div>

            </div>

            <div class="grid place-items-center">
                <img src={Faketoshi} alt="Faketoshi being kicked">
            </div>
            </div>
        </div>
    </div>
    <div class="md:w-2/3 items-center mx-auto mt-20">
        <div class="grid">
            <!-- AVATARS -->
            <div class="grid lg:grid-cols-5 grid-cols-3 gap-4 place-items-center lg:w-1/2 w-full mx-auto">
                {#each featuredAuctionAvatars as avatar}
                    <div class="avatar">
                        <div class="w-16 rounded-full ring ring-accent ring-offset-base-100 ring-offset-2">
                            <a href="/auctions/{avatar.entity_key}">
                                <img src={avatar.url} alt="featured avatar" />
                            </a>
                        </div>
                    </div>
                {/each}
            </div>

            <div class="grid lg:grid-cols-2 gap-8 my-12 p-4">
              <!-- COL -->
                <div class="w-full">
                    <h2 class="lg:text-5xl text-4xl font-bold">{title}</h2>
                    {#if description}
                        <div class="markdown-container leading-8 my-4">
                            <SvelteMarkdown source={description} />
                        </div>
                    {/if}

                    <!-- TELEGRAM AND TWITTER -->
                    <div class="flex flex-col gap-4 w-full py-4 my-4">
                      <ExternalLinks {owner} />
                  </div>
                </div>

                <!-- COL -->
                <div class="grid place-items-center border-l border-gray-700/40 p-4">
                    <slot name="extra-description" />
                </div>
            </div>
        </div>
    </div>
{/if}

<!-- ITEM LISTS -->
<div id="anchorIdAuctionTime" class="lg:flex lg:w-2/3 mx-auto my-4">
    <div class="w-full px-4">
        {#if canAddItems || showActiveAuctions || showPastAuctions}
            <h3 id="anchorId" class="text-sm uppercase font-black lg:text-start text-center">Auctions</h3>
            {#if canAddItems}
                <ListView
                    bind:this={auctionsLists['new']}
                    loader={{endpoint: `${baseUrl}/auctions?filter=new`, responseField: 'auctions', fromJson: auctionFromJson}}
                    postEndpoint={`${baseUrl}/auctions`}
                    onSave={onAuctionSave}
                    {onForceReload}
                    editor={AuctionEditor}
                    {showItemsCampaign}
                    card={ItemCard}
                    style={ListViewStyle.Grid}>
                    <div slot="new-entity" class="lg:flex items-center lg:justify-start justify-center my-4 lg:space-x-4 lg:space-y-0 space-y-2" let:setCurrent={setCurrent}>
                        {#if isCampaignStall}
                            <div id="auction-hour-1">
                                <div class="grid place-items-center">
                                    <button class="btn btn-primary font-bold text-center w-52" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new TimeAuction())}>1 Hour of your time</button>
                                </div>
                            </div>
                        {/if}
                        <div id="anchorIdAuctionItem" class="grid lg:place-items-start place-items-center w-full">
                            <div class="w-full flex lg:justify-start justify-center">
                                <button class="btn btn-secondary font-bold text-center w-48" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new Auction())}>Auction Item</button>
                            </div>
                        </div>
                    </div>
                </ListView>
            {/if}
            {#if showActiveAuctions || showPastAuctions}
                <div class="tabs lg:flex lg:justify-start justify-center">
                    {#each availableFilters as filter}
                        <a href="#{filter}" class="text-2xl tab tab-bordered" class:tab-active={auctionFilter === filter} on:click={() => auctionFilter = filter}>{filter}</a>
                    {/each}
                </div>
                {#each availableFilters as filter}
                    <div class="" class:hidden={auctionFilter !== filter}>
                        <ListView
                            bind:this={auctionsLists[filter]}
                            loader={{endpoint: `${baseUrl}/auctions?filter=${filter}`, responseField: 'auctions', fromJson: auctionFromJson}}
                            onSave={onAuctionSave}
                            {onForceReload}
                            editor={canAddItems ? AuctionEditor : null}
                            {showItemsCampaign}
                            card={ItemCard}
                            style={ListViewStyle.Grid} />
                    </div>
                {/each}
            {/if}
            <div class="divider"></div>
        {/if}
        {#if canAddItems || showActiveListings || showPastListings}
            <h3 id="anchorIdFixedPrice" class="text-sm uppercase font-black lg:text-start text-center">Fixed price</h3>
            {#if canAddItems}
                <ListView
                    bind:this={listingsLists['new']}
                    loader={{endpoint: `${baseUrl}/listings?filter=new`, responseField: 'listings', fromJson: listingFromJson}}
                    postEndpoint={`${baseUrl}/listings`}
                    onSave={onListingSave}
                    {onForceReload}
                    editor={ListingEditor}
                    {showItemsCampaign}
                    card={ItemCard}
                    style={ListViewStyle.Grid}>
                    <div slot="new-entity" class="flex justify-start" let:setCurrent={setCurrent}>
                        <div class="w-full flex lg:justify-start justify-center">
                            <button class="btn btn-secondary font-bold text-center w-48 my-4" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new Listing())}>Sell Item</button>
                        </div>
                    </div>
                </ListView>
            {/if}
            {#if showActiveListings || showPastListings}
                <div class="tabs flex lg:justify-start justify-center">
                    {#each availableFilters as filter}
                        <a href="#{filter}" class="text-2xl tab tab-bordered" class:tab-active={listingFilter === filter} on:click={() => listingFilter = filter}>{filter}</a>
                    {/each}
                </div>
                {#each availableFilters as filter}
                    <div class="" class:hidden={listingFilter !== filter}>
                        <ListView
                            bind:this={listingsLists[filter]}
                            loader={{endpoint: `${baseUrl}/listings?filter=${filter}`, responseField: 'listings', fromJson: listingFromJson}}
                            onSave={onListingSave}
                            {onForceReload}
                            editor={canAddItems ? ListingEditor : null}
                            {showItemsCampaign}
                            card={ItemCard}
                            style={ListViewStyle.Grid} />
                    </div>
                {/each}
            {/if}
        {/if}
    </div>
</div>
