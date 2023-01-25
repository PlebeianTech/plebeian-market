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
    import { getChannelIdFromChannelName } from '$lib/nostr/utils'
    // import CampaignStats from './CampaignStats.svelte';
    import Avatar from './Avatar.svelte';

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

    $: telegramUsername = owner ? owner.telegramUsername : null;
    $: telegramHref = owner && telegramUsername ? `https://t.me/${owner.telegramUsername}` : null;

    $: twitterUsername = owner ? owner.twitterUsername : null;
    $: twitterHref = owner && twitterUsername ? `https://twitter.com/${owner.twitterUsername}` : null;

    let nostrChannelName = null;
    let nostrRoomId: string = null;
    if (owner) {
        // TODO: we need a unique static ID to use here
        nostrChannelName = 'Plebeian Market Stall ' + owner.nym + ' (' + import.meta.env.MODE + ')';
        nostrRoomId = getChannelIdFromChannelName(nostrChannelName);
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

    let AvatarSize: number = 20
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
    <div class="absolute inset-x-0 lg:bottom-1/4 m-auto left-0 right-0 lg:w-2/3 mx-auto z-40">
      <div class="grid lg:grid-cols-2 gap-4">
        <!-- COL1 -->
        <div class="lg:flex space-x-8 items-center w-full">
          <div class="grid place-items-center my-4">
            {#if owner}
                <Avatar account={owner} size={AvatarSize} />
            {/if}
          </div>
          <div class="grid lg:place-items-start place-items-center">
            <h2 class="lg:text-5xl text-4xl font-bold">{title}</h2>
            {#if description}
                <div class="markdown-container leading-8 my-4">
                    <SvelteMarkdown source={description} />
                </div>
            {/if}
            <div class="lg:flex items-center lg:space-x-2">
              <!-- TELEGRAM -->
              {#if telegramHref}
                  <a href={telegramHref} class="link text-2xl flex items-center space-x-2" target="_blank" rel="noreferrer">
                      <span class="flex items-center justify-center">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-telegram" viewBox="0 0 16 16">
                              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.05-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09z"/>
                          </svg>
                      </span>
                      <span class="flex items-center justify-center">
                          @{telegramUsername}
                      </span>
                  </a>
              {/if}
              <!-- TWITTER -->
              {#if twitterHref}
                <a href={twitterHref} class="link text-2xl flex items-center space-x-2" target="_blank" rel="noreferrer">
                    <span class="flex items-center justify-center">
                        <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
                            <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                        </svg>
                    </span>
                    <span class="flex items-center justify-center">
                        @{twitterUsername}
                    </span>
                </a>
              {/if}
                <!-- NOSTR -->
                
            </div>
          </div>
        </div>
        <!-- COL2 -->
        <div class="grid lg:place-items-end place-items-center">
          <div>
            <div class="dropdown">
              <label tabindex="0" class="btn btn-primary m-1">Add New 
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
              </svg>
              </label>
              <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52">
                <!-- <li><a>Auction Hour</a></li> -->
                <li><a>Auction Item</a></li>
                <li><a>Sell Item</a></li>
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
    <div class="w-full inline-block lg:h-96 relative after:pt-[33.33%] after:block after:content-['']">
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


<div class="lg::w-2/3 items-center mx-auto">
    <div class="grid">
        <!-- <div class="mt-4 text-center">
            {#if owner}
                <Avatar account={owner} size={AvatarSize} />
            {/if}
        </div> -->
        <!-- AVATARS -->
        <div class="grid lg:grid-cols-5 grid-cols-3 gap-4 place-items-center lg:w-1/2 w-full mx-auto my-8">
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


          <!-- {#if editUrl}
              <a href={editUrl} class="btn btn-outline text-sm uppercase font-bold my-2">Edit Page</a>
          {/if} -->
  

        <div class="grid place-items-center gap-8 my-12 p-4">
          <!-- COL -->
            <div id="bgXPUB" class="grid place-items-center lg:w-2/3 mx-auto">
              {#if isCampaignStall}
              <div class="grid lg:grid-cols-2 border border-gray-500/70 rounded shadow-xl gap-4">
                  <!-- CAMPAIGN INFO -->
                  <div class="grid place-items-center p-4">
                    <div class="w-full">
                      <h2 class="lg:text-5xl text-4xl font-bold">{title}</h2>
                      {#if description}
                          <div class="markdown-container leading-8 my-4">
                              <SvelteMarkdown source={description} />
                          </div>
                      {/if}
    
                    <div class="flex flex-col gap-4 w-full py-4 my-4">
                      <div class="lg:flex lg:space-x-4 lg:space-y-0 space-y-2">
                          {#if telegramHref}
                              <a href={telegramHref} class="link text-2xl flex items-center space-x-2" target="_blank" rel="noreferrer">
                                  <span class="flex items-center justify-center">
                                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-telegram" viewBox="0 0 16 16">
                                          <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.05-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09z"/>
                                      </svg>
                                  </span>
                                  <span class="flex items-center justify-center">
                                      @{telegramUsername}
                                  </span>
                              </a>
                          {/if}
                          {#if twitterHref}
                            <a href={twitterHref} class="link text-2xl flex items-center space-x-2" target="_blank" rel="noreferrer">
                                <span class="flex items-center justify-center">
                                    <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
                                        <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                                    </svg>
                                </span>
                                <span class="flex items-center justify-center">
                                    @{twitterUsername}
                                </span>
                            </a>
                          {/if}
                      </div>
                      
                       <!-- EDIT BUTTON -->
                       {#if editUrl}
                          <a href={editUrl}>
                            <button class="btn btn-secondary text-sm uppercase font-bold my-2">
                              Edit info
                            </button>
                          </a>
                      {/if}

                  </div>
                </div>
                </div>
                <!-- XPUB -->
                <div>
                  <slot name="extra-description" />
                </div>
              </div>
              {:else}
                <div class="flex flex-col gap-4 ml-2">
                  {#if badges.length !== 0}
                      <h2 class="text-2xl font-bold text-center my-4">Badges</h2>
                      <div class="flex gap-2">
                          {#each badges as badge}
                              <BadgeSVG {badge} />
                          {/each}
                      </div>
                  {/if}
                </div>
              {/if}
            </div>
        </div>
    </div>
</div>

<!-- LIST -->
<div id="anchorIdAuctionTime" class="lg:flex lg:w-2/3 mx-auto">
    <div class="flex w-full">
      <!-- AUCTIONS -->
      <div class="w-full">
        {#if canAddItems || showActiveAuctions || showPastAuctions}
            <h3 id="anchorId" class="text-sm uppercase lg:text-start font-black text-center">Auctions</h3>
            
            <!-- TABS -->
            {#if showActiveAuctions || showPastAuctions}
                <div class="tabs flex lg:justify-start justify-center">
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

            <!-- LIST -->
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
                    <div slot="new-entity" class="flex lg:justify-start justify-center" let:setCurrent={setCurrent}>
                        {#if isCampaignStall}
                            <div id="auction-hour-1" class=" grid lg:place-items-start p-4" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new TimeAuction())}>
                              <div class="w-full my-8">
                                <!-- <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width={1.5} stroke="currentColor" class="w-24 h-24">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg> -->
                                <p class="btn btn-primary font-bold text-center">1 Hour of your time</p>
                              </div>
                            </div>
                        {/if}

                        <div id="anchorIdAuctionItem" class="p-4" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new Auction())}>
                          <div class="w-full  my-8">
                            <!-- <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-24 h-24">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3.75v16.5M2.25 12h19.5M6.375 17.25a4.875 4.875 0 004.875-4.875V12m6.375 5.25a4.875 4.875 0 01-4.875-4.875V12m-9 8.25h16.5a1.5 1.5 0 001.5-1.5V5.25a1.5 1.5 0 00-1.5-1.5H3.75a1.5 1.5 0 00-1.5 1.5v13.5a1.5 1.5 0 001.5 1.5zm12.621-9.44c-1.409 1.41-4.242 1.061-4.242 1.061s-.349-2.833 1.06-4.242a2.25 2.25 0 013.182 3.182zM10.773 7.63c1.409 1.409 1.06 4.242 1.06 4.242S9 12.22 7.592 10.811a2.25 2.25 0 113.182-3.182z" />
                            </svg> -->
                            <p class="btn btn-secondary font-bold text-center w-48">Auction Item</p>
                          </div>
                        </div>
                    </div>
                </ListView>
            {/if}
        {/if}
        
        <div class="divider"></div>

        <!-- FIXED PRICE  -->
        {#if canAddItems || showActiveListings || showPastListings}
            <h3 id="anchorIdFixedPrice" class="text-sm uppercase lg:text-start font-black text-center">Fixed price</h3>
            
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
                        <div class="mx-auto my-10 w-full flex lg:justify-start justify-center p-4" on:click|preventDefault={() => loginAndNewItem(setCurrent, () => new Listing())}>
                          <!-- <div class="w-20 my-8">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3.75v16.5M2.25 12h19.5M6.375 17.25a4.875 4.875 0 004.875-4.875V12m6.375 5.25a4.875 4.875 0 01-4.875-4.875V12m-9 8.25h16.5a1.5 1.5 0 001.5-1.5V5.25a1.5 1.5 0 00-1.5-1.5H3.75a1.5 1.5 0 00-1.5 1.5v13.5a1.5 1.5 0 001.5 1.5zm12.621-9.44c-1.409 1.41-4.242 1.061-4.242 1.061s-.349-2.833 1.06-4.242a2.25 2.25 0 013.182 3.182zM10.773 7.63c1.409 1.409 1.06 4.242 1.06 4.242S9 12.22 7.592 10.811a2.25 2.25 0 113.182-3.182z" />
                            </svg>
                          </div> -->
                          <p class="btn btn-secondary font-bold text-center w-48">Sell Item</p>
                        </div>
                    </div>
                </ListView>
            {/if}
            
        {/if}
      </div>

    </div>

    <!-- NOSTR CHAT  -->
    {#if !isProduction() }
    <div class="lg:w-3/6 my-2 grid place-items-top lg:h-3/4 sticky top-24 p-4 overflow-y-scroll">
      <!-- <h3 class="text-4xl font-black text-center">Nostr Chat</h3> -->
          <NostrChat
              emptyChatShowsLoading={false}
              messageLimit={500}
              {nostrRoomId}
          />
    </div>
    {/if}
</div>
