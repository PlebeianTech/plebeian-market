<script lang="ts">
    import SvelteMarkdown from 'svelte-markdown';
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import Avatar, { AvatarSize } from "$lib/components/Avatar.svelte";
    import BadgeSVG from "$lib/components/BadgeSVG.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ItemCardSmall from "$lib/components/ItemCardSmall.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import Login from "$lib/components/Login.svelte";
    import { publish } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction, TimeAuction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import type { IAccount, Badge, User } from "$lib/types/user";
    import { Category } from '$lib/types/item';
    import HeroImage from "$lib/images/hodlonaut-faketoshi.svg"
   
    export let baseUrl: string;

    export let bannerUrl: string | null;
    export let owner: IAccount | null;
    export let title: string;
    export let description: string | null;
    export let editUrl: string | null = null;

    export let badges: Badge[] = [];

    export let isOwnStall = false;
    export let isCampaignStall = false;

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
                    Info.set("Your auction is live!");
                    onForceReload();
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

    let onLogin: ((_: User | null) => void) | null = null;

    function newItem(setCurrent: (IEntity) => void, getNewItem: () => IEntity) {
        if ($user && $user.nym) {
            setCurrent(getNewItem());
        } else {
            onLogin = (_: User | null) => {
                onLogin = null;
                setCurrent(getNewItem());
                if (isCampaignStall) {
                    localStorage.setItem('initial-login-campaign', "1");
                }
            };
        }
    }

    function scrollIntoView({ target }) {
      const el = document.querySelector(target.getAttribute('href'))
      if (!el) return;
      el.scrollIntoView({
        behavior: 'smooth'
      })
    }
</script>

<svelte:head>
  <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
</svelte:head>

{#if isCampaignStall}
  <!-- HERO SECTION STATIC CONTENT -->
  <div id="bgHero" class="bg-fixed">
    <!-- FILTER -->
    <div class="bg-black/20">
      <!-- HERO -->
      <div class="lg:w-2/3 mx-auto grid lg:grid-cols-2 gap-4">
        <!-- COL -->
        <div class="mt-20 p-4">
          <!-- FULL WIDTH BANNER -->
          <!-- <img src={BannerImg} alt=""> -->
          <h2 class="lg:text-7xl text-4xl font-bold">{title}</h2>
          <!-- <h1 class="lg:text-2xl font-bold mt-4">Get started</h1> -->
          <a href="#anchorIdAuctionTime" on:click|preventDefault={scrollIntoView} class="btn btn-primary uppercase font-bold my-8">Auction 1-hour of your time</a>
          <div class="mb-8">
            <!-- <p class="text-3xl">OR</p> -->
            <div class="space-x-1">
              <a href="#anchorIdAuctionItem" on:click|preventDefault={scrollIntoView} class="btn btn-outline uppercase font-bold my-4">Auction Item</a>
              <a href="#anchorIdFixedPrice" on:click|preventDefault={scrollIntoView} class="btn btn-outline uppercase font-bold my-4">Fixed Price</a>
            </div>
          </div>
    
          <!-- AVATARS -->
          <div class="flex space-x-4">
            <div class="avatar flex">
              <div class="w-16 rounded">
                <img src="https://placeimg.com/192/192/people" alt="image" />
              </div>
            </div>
            <div class="avatar">
              <div class="w-16 rounded">
                <img src="https://placeimg.com/192/192/people" alt="Tailwind-CSS-Avatar-component" />
              </div>
            </div>
            <div class="avatar">
              <div class="w-16 rounded">
                <img src="https://placeimg.com/192/192/people" alt="Tailwind-CSS-Avatar-component" />
              </div>
            </div>
          </div>
          
          <div class="my-4">
            <!-- <lottie-player
              src="https://assets1.lottiefiles.com/packages/lf20_6mveojb1.json"
              background="transparent"
              speed="1"
              loop
              autoplay
              class=""
              style="width: 100px; height: 100px"
            ></lottie-player> -->
          </div>
        </div>
    
        <div class="grid place-items-center">
          <img src={HeroImage} alt="hero-image">
        </div>
        </div>
   
    </div>
    </div>
{:else}
<!-- always keep a 3:1 aspect ratio, see https://stackoverflow.com/a/12121309 -->
<div class="lg:w-2/3 mx-auto">
  <div class="w-full inline-block relative after:pt-[33.33%] after:block after:content-[''] lg:mt-24 mt-12">
        <div class="absolute top-0 bottom-0 left-0 right-0 rounded-md bg-center bg-no-repeat bg-cover" style="background-image: url({bannerUrl});" alt=""></div>
    </div>
</div>
{/if}


<div class="md:w-2/3 items-center mx-auto mt-20">
    <!-- always keep a 3:1 aspect ratio, see https://stackoverflow.com/a/12121309 -->
    <!-- <div class="w-full inline-block relative after:pt-[33.33%] after:block after:content-[''] lg:mt-24 mt-12">
        <div class="absolute top-0 bottom-0 left-0 right-0 rounded-md bg-center bg-no-repeat bg-cover" style="background-image: url({bannerUrl});" alt=""></div>
    </div> -->


    <div class="grid">

        <!-- <div class="mt-4 text-center">
            {#if owner}
                <Avatar account={owner} size={AvatarSize.L} />
            {/if}
        </div> -->
        <div class="flex justify-end my-4 border-b border-gray-700/20 py-2">
          {#if editUrl}
              <a href={editUrl} class="btn btn-ghost text-sm uppercase font-bold mt-2">Edit</a>
          {/if}
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

                <div class="flex flex-col gap-4 border-t border-gray-700/40 w-full py-4 my-4">
                  <div class="flex space-x-4">
                      {#if telegramHref}
                          <a href={telegramHref} class="link text-2xl" target="_blank" rel="noreferrer">
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
              </div>
                
                <div class="flex flex-col gap-4 ml-2">
                    {#if badges.length !== 0}
                        <div>Badges</div>
                        <div class="flex gap-2">
                            {#each badges as badge}
                                <BadgeSVG {badge} />
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>
            <!-- COL -->
            <div id="bgXPUB" class="grid place-items-top border border-gray-700/40 rounded p-4">
                <slot name="extra-description" />
            </div>
        </div>
    </div>    
   
</div>


<div id="anchorIdAuctionTime" class="md:flex lg:w-2/3 mx-auto my-12">
    <div class="md:grow">
        {#if onLogin !== null}
            <Login {onLogin} />
        {/if}
        {#if canAddItems || showActiveAuctions || showPastAuctions}
            <h3 class="lg:text-8xl text-4xl font-black text-center my-8">Auctions</h3>
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
                    <div slot="new-entity" class="lg:flex justify-center" let:setCurrent={setCurrent}>
                        {#if isCampaignStall}
                            <div id="auction-hour-1" class="grid place-items-center mx-auto my-10 border border-gray-700/40 p-4" on:click|preventDefault={() => newItem(setCurrent, () => new TimeAuction())}>
                              <div class="w-20 my-8">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width={1.5} stroke="currentColor" className="w-6 h-6">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                              </div>
                              <p class="btn btn-primary font-bold text-center">1 Hour of time</p>
                            </div>
                        {/if}
                        <div id="anchorIdAuctionItem" class="grid place-items-center mx-auto my-10 border border-gray-700/40 p-4" on:click|preventDefault={() => newItem(setCurrent, () => new Auction())}>
                          
                          <div class="w-20 my-8">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3.75v16.5M2.25 12h19.5M6.375 17.25a4.875 4.875 0 004.875-4.875V12m6.375 5.25a4.875 4.875 0 01-4.875-4.875V12m-9 8.25h16.5a1.5 1.5 0 001.5-1.5V5.25a1.5 1.5 0 00-1.5-1.5H3.75a1.5 1.5 0 00-1.5 1.5v13.5a1.5 1.5 0 001.5 1.5zm12.621-9.44c-1.409 1.41-4.242 1.061-4.242 1.061s-.349-2.833 1.06-4.242a2.25 2.25 0 013.182 3.182zM10.773 7.63c1.409 1.409 1.06 4.242 1.06 4.242S9 12.22 7.592 10.811a2.25 2.25 0 113.182-3.182z" />
                            </svg>
                                                      
                          </div>
                          
                          <p class="btn btn-secondary font-bold text-center">Physical Item</p>
                        </div>
                    </div>
                </ListView>
            {/if}
            {#if showActiveAuctions || showPastAuctions}
                <div class="tabs flex justify-center my-12">
                    {#each availableFilters as filter}
                        <a href="#{filter}" class="text-2xl tab tab-lifted" class:tab-active={auctionFilter === filter} on:click={() => auctionFilter = filter}>{filter}</a>
                    {/each}
                </div>
                {#each availableFilters as filter}
                    <div class="bg-base-200" class:hidden={auctionFilter !== filter}>
                        <ListView
                            bind:this={auctionsLists[filter]}
                            loader={{endpoint: `${baseUrl}/auctions?filter=${filter}`, responseField: 'auctions', fromJson: auctionFromJson}}
                            {onForceReload}
                            editor={null}
                            {showItemsOwner} {showItemsCampaign}
                            card={ItemCardSmall}
                            style={ListViewStyle.Grid} />
                    </div>
                {/each}
            {/if}
            <div class="divider my-20"></div>
        {/if}
        {#if canAddItems || showActiveListings || showPastListings}
            <h3 id="anchorIdFixedPrice" class="lg:text-8xl text-4xl font-black text-center">Fixed price</h3>
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
                    <div slot="new-entity" class="flex flex-col md:flex-row" let:setCurrent={setCurrent}>
                        <div class="mx-auto my-10 grid place-items-center w-full lg:w-1/3 border border-gray-700/40 p-4" on:click|preventDefault={() => newItem(setCurrent, () => new Listing())}>
                          <div class="w-20 my-8">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="w-6 h-6">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M12 3.75v16.5M2.25 12h19.5M6.375 17.25a4.875 4.875 0 004.875-4.875V12m6.375 5.25a4.875 4.875 0 01-4.875-4.875V12m-9 8.25h16.5a1.5 1.5 0 001.5-1.5V5.25a1.5 1.5 0 00-1.5-1.5H3.75a1.5 1.5 0 00-1.5 1.5v13.5a1.5 1.5 0 001.5 1.5zm12.621-9.44c-1.409 1.41-4.242 1.061-4.242 1.061s-.349-2.833 1.06-4.242a2.25 2.25 0 013.182 3.182zM10.773 7.63c1.409 1.409 1.06 4.242 1.06 4.242S9 12.22 7.592 10.811a2.25 2.25 0 113.182-3.182z" />
                            </svg>
                                                      
                          </div>
                          <p class="btn btn-secondary font-bold text-center">Sell Item</p>
                        </div>
                    </div>
                </ListView>
            {/if}
            {#if showActiveListings || showPastListings}
                <div class="tabs flex justify-center">
                    {#each availableFilters as filter}
                        <a href="#{filter}" class="text-2xl tab tab-lifted" class:tab-active={listingFilter === filter} on:click={() => listingFilter = filter}>{filter}</a>
                    {/each}
                </div>
                {#each availableFilters as filter}
                    <div class="bg-base-200" class:hidden={listingFilter !== filter}>
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
</div>

