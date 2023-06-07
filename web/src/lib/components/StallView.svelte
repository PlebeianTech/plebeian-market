<script lang="ts">
    import { onMount } from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';
    import { goto } from "$app/navigation";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import BadgeSVG from "$lib/components/BadgeSVG.svelte";
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
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import { getChannelIdForStallOwner } from '$lib/nostr/utils'
    import Avatar, {AvatarSize} from './Avatar.svelte';
    import ExternalLinks from './externalLinks.svelte';
    import Spaceship from "$lib/images/spaceship.jpg";

    export let baseUrl: string;

    export let bannerUrl: string | null;
    export let owner: IAccount | null;
    export let title: string;
    export let description: string | null;
    export let editUrl: string | null = null;

    export let badges: Badge[] = [];

    export let isOwnStall = false;
    export let isCampaignStall = false;
    export let campaignKey: string | null = null;

    export let showItemsOwner: boolean;
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

    let nostrRoomId: string | null = null;
    if (owner) {
        nostrRoomId = getChannelIdForStallOwner(owner);
    }

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
{:else}
    <!-- always keep a 3:1 aspect ratio, see https://stackoverflow.com/a/12121309 -->
    <div class="mx-auto relative lg:mb-0 mb-6">
        <div class="absolute inset-x-0 lg:bottom-20 m-auto left-0 right-0 lg:w-2/3 mx-auto z-40">
            <div class="grid lg:grid-cols-2 gap-4">
                <!-- COL1 -->
                <div class="lg:flex space-x-8 items-center w-full">
                    <div class="grid lg:place-items-start place-items-center">
                        <div class="grid place-items-center my-4">
                        {#if owner}
                            <Avatar account={owner} size={AvatarSize.M}  />
                        {/if}
                        </div>
                        <h2 class="lg:text-5xl text-4xl font-bold">{title}</h2>
                        {#if description}
                            <div class="markdown-container leading-8 my-2 lg:text-left text-center p-1">
                                <SvelteMarkdown source={description} />
                            </div>
                        {/if}

                        <!-- TELEGRAM AND TWITTER -->
                        <div>
                            <ExternalLinks {owner} />
                        </div>

                        <!-- BADGES -->
                        <div class="grid lg:place-items-start place-items-center my-4 w-full">
                        {#if badges.length !== 0}
                            <h2 class="text-sm uppercase font-bold text-center my-4">Badges</h2>
                            <div class="flex gap-2">
                                {#each badges as badge}
                                    <BadgeSVG {badge} />
                                {/each}
                            </div>
                        {/if}
                        </div>
                    </div>
                </div>
                <!-- COL2 -->
                <div class="grid lg:place-items-end place-items-center">
                <div>
                    <!-- ADD NEW -->
                    <div class="dropdown">
                    <label tabindex="0" class="btn btn-primary m-1">Add New
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                        </svg>
                    </label>
                    <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52">
                        <li><a href="#anchorId" on:click|preventDefault={loginAndScrollIntoView}>Auction Item</a></li>
                        <li><a href="#anchorIdFixedPrice" on:click|preventDefault={loginAndScrollIntoView}>Sell Item</a></li>
                    </ul>
                    </div>
                    {#if editUrl}
                        <a href={editUrl} class="btn btn-outline text-sm uppercase font-bold my-2">Edit Page</a>
                    {/if}
                </div>
                </div>
            </div>
        </div>
        <!-- BG IMAGE -->
        <div id="stallHeroImageHeight" class="lg:h-1/2 h-screen w-full inline-block relative after:pt-[33.33%] after:block after:content-['']">
            <div class="absolute top-0 bottom-0 left-0 right-0 rounded-md bg-center bg-no-repeat bg-cover opacity-20" style="background-image: url('{bannerUrl}')"></div>
        </div>
    </div>
{/if}

{#if isCampaignStall}
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
                    {showItemsOwner} {showItemsCampaign}
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
                            {showItemsOwner} {showItemsCampaign}
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
                    {showItemsOwner} {showItemsCampaign}
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
                            {showItemsOwner} {showItemsCampaign}
                            card={ItemCard}
                            style={ListViewStyle.Grid} />
                    </div>
                {/each}
            {/if}
        {/if}
    </div>

    <!-- NOSTR -->
    {#if !isCampaignStall}
        <div class="lg:w-3/6 max-h-screen overflow-y-auto lg:overflow-y-hidden my-2 grid place-items-top top-20 lg:px-0 px-2" id="stallChatContainerDiv">
            <h3 class="text-2xl lg:text-4xl fontbold mt-0 lg:mt-8 mb-2">Stall Chat</h3>

            {#if nostrRoomId !== null}
                <NostrChat messageLimit={500} {nostrRoomId} />
            {/if}
        </div>
    {/if}
</div>
