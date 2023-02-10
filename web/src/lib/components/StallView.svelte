<script lang="ts">
    import { onMount } from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';
    import { goto } from "$app/navigation";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import BadgeSVG from "$lib/components/BadgeSVG.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ItemCardSmall from "$lib/components/ItemCardSmall.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import { publish, getFeaturedAvatars } from "$lib/services/api";
    import {Info, token, user} from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction, TimeAuction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import type { IAccount, Badge, User } from "$lib/types/user";
    import { Category } from '$lib/types/item';
    import Faketoshi from "$lib/images/Bitko-Illustration-Faketoshi.svg"
    import {requestLoginModal} from "../utils";
    import NostrChat from "$lib/components/NostrChat.svelte";
    import { isProduction } from "$lib/utils";
    import { getChannelIdForStallOwner } from '$lib/nostr/utils'
    // import CampaignStats from './CampaignStats.svelte';
    import Avatar, {AvatarSize} from './Avatar.svelte';
    import ExternalLinks from './externalLinks.svelte';

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

    let nostrRoomId: string = null;
    if (owner) {
        nostrRoomId = getChannelIdForStallOwner(owner);
    }

    function onAuctionCreated(key: string, entity: IEntity) {
        user.update((u) => {
            u!.hasItems = true;
            if (isOwnStall) {
                u!.hasOwnItems = true;
            }
            return u;
        });
        let auction = entity as Auction;
        if (auction.category === Category.Time) {
            publish($token, auction.endpoint, key, false,
                () => {
                    onForceReload();
                    goto(`/auctions/${key}`);
                });
        } else {
            Info.set("Your auction will start when we verify your tweet!");
        }
    }

    function onListingCreated(_: string, __: IEntity) {
        user.update((u) => {
            u!.hasItems = true;
            if (isOwnStall) {
                u!.hasOwnItems = true;
            }
            return u;
        });
        Info.set("Your listing will become active after we verify your tweet!");
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
            requestLoginModal(() => setCurrent(getNewItem()));
        }
    }

    function loginAndScrollIntoView({ target }) {
        if ($user && $user.nym) {
            scrollIntoView(target);
        } else {
            requestLoginModal(() => scrollIntoView(target));
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
  <div id="bgHero" class="bg-fixed">
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
          <img src={Faketoshi} alt="hero-image">
        </div>
        </div>
    </div>
  </div>

  <!-- <CampaignStats /> -->
{:else}
 <!-- always keep a 3:1 aspect ratio, see https://stackoverflow.com/a/12121309 -->
 <div class="mx-auto relative lg:mb-0 mb-36">
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
        <div class="absolute top-0 bottom-0 left-0 right-0 rounded-md bg-center bg-no-repeat bg-cover opacity-20" style="background-image: url({bannerUrl});" alt="twitter banner"></div>
    </div>
</div>
{/if}

<style>
  #bgHero {
    background-image: url('$lib/images/spaceship.jpg');
    background-repeat: no-repeat;
    background-size: cover;
    background-position: bottom;
  }
  
</style>


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

        {#if isCampaignStall}
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
            <div id="bgXPUB" class="grid place-items-center border-l border-gray-700/40 p-4">
                <slot name="extra-description" />                
            </div>
        </div>
        {/if}
    </div>
</div>

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
                    onCreated={onAuctionCreated}
                    {onForceReload}
                    editor={AuctionEditor}
                    {showItemsOwner} {showItemsCampaign}
                    card={ItemCard}
                    style={ListViewStyle.List}>
                    <div slot="new-entity" class="lg:flex items-center lg:justify-start justify-center my-4 lg:space-x-4 lg:space-y-0 space-y-2" let:setCurrent={setCurrent}>
                        {#if isCampaignStall}
                            <div id="auction-hour-1" class="" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new TimeAuction())}>
                              <div class="grid place-items-center">
                                <!-- <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width={1.5} stroke="currentColor" class="w-24 h-24">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg> -->
                                <button class="btn btn-primary font-bold text-center w-52">1 Hour of your time</button>
                              </div>
                            </div>
                        {/if}

                        <div id="anchorIdAuctionItem" class="grid lg:place-items-start place-items-center w-full" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new Auction())}>
                          <div class="w-full flex lg:justify-start justify-center">
                            <!-- <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-24 h-24">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3.75v16.5M2.25 12h19.5M6.375 17.25a4.875 4.875 0 004.875-4.875V12m6.375 5.25a4.875 4.875 0 01-4.875-4.875V12m-9 8.25h16.5a1.5 1.5 0 001.5-1.5V5.25a1.5 1.5 0 00-1.5-1.5H3.75a1.5 1.5 0 00-1.5 1.5v13.5a1.5 1.5 0 001.5 1.5zm12.621-9.44c-1.409 1.41-4.242 1.061-4.242 1.061s-.349-2.833 1.06-4.242a2.25 2.25 0 013.182 3.182zM10.773 7.63c1.409 1.409 1.06 4.242 1.06 4.242S9 12.22 7.592 10.811a2.25 2.25 0 113.182-3.182z" />
                            </svg> -->
                            <button class="btn btn-secondary font-bold text-center w-48">Auction Item</button>
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
                            {onForceReload}
                            editor={canAddItems ? AuctionEditor : null}
                            {showItemsOwner} {showItemsCampaign}
                            card={ItemCardSmall}
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
                    onCreated={onListingCreated}
                    {onForceReload}
                    editor={ListingEditor}
                    {showItemsOwner} {showItemsCampaign}
                    card={ItemCard}
                    style={ListViewStyle.List}>
                    <div slot="new-entity" class="flex justify-start" let:setCurrent={setCurrent}>
                        <div class="w-full flex lg:justify-start justify-center" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new Listing())}>
                          <!-- <div class="w-20 my-8">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3.75v16.5M2.25 12h19.5M6.375 17.25a4.875 4.875 0 004.875-4.875V12m6.375 5.25a4.875 4.875 0 01-4.875-4.875V12m-9 8.25h16.5a1.5 1.5 0 001.5-1.5V5.25a1.5 1.5 0 00-1.5-1.5H3.75a1.5 1.5 0 00-1.5 1.5v13.5a1.5 1.5 0 001.5 1.5zm12.621-9.44c-1.409 1.41-4.242 1.061-4.242 1.061s-.349-2.833 1.06-4.242a2.25 2.25 0 013.182 3.182zM10.773 7.63c1.409 1.409 1.06 4.242 1.06 4.242S9 12.22 7.592 10.811a2.25 2.25 0 113.182-3.182z" />
                            </svg>
                          </div> -->
                          <p class="btn btn-secondary font-bold text-center w-48 my-4">Sell Item</p>
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
                            {onForceReload}
                            editor={canAddItems ? ListingEditor : null}
                            {showItemsOwner} {showItemsCampaign}
                            card={ItemCardSmall}
                            style={ListViewStyle.Grid} />
                    </div>
                {/each}
            {/if}
        {/if}

      </div>

      <!-- NOSTR -->
      {#if !isProduction() }
          <div class="lg:w-3/6 my-2 grid place-items-top lg:h-1/2 sticky top-20 lg:px-0 px-2">
              <NostrChat
                  emptyChatShowsLoading={false}
                  messageLimit={500}
                  {nostrRoomId}
              />
          </div>
      {/if}
</div>
