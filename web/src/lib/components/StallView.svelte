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
    import BannerImg from "$lib/images/banner-100.jpg"
   
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

<div class="w-11/12 md:w-2/3 items-center mx-auto mt-2">

  <!-- HERO -->
  <div class="grid my-12">
    <div class="grid place-items-center">
      <img src={BannerImg} alt="">
    </div>
    <div class="grid place-items-center w-full my-12">
      <h1 class="lg:text-4xl font-bold my-8">Get started</h1>
      <a href="#anchorId" on:click|preventDefault={scrollIntoView} class="btn btn-primary uppercase font-bold">Auction 1-hour of your time</a>
      <lottie-player
        src="https://assets1.lottiefiles.com/packages/lf20_vfmyxu76.json"
        background="transparent"
        speed="1"
        loop
        autoplay
        class="opacity-50"
        style="width: 100px; height: 100px"
      ></lottie-player>
    </div>
  </div>
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
        <div class="flex justify-end my-4 border-b border-gray-700/20 py-4">
          {#if editUrl}
              <a href={editUrl} class="btn btn-ghost text-sm uppercase font-bold mt-2">Edit</a>
          {/if}
        </div>
        <div class="grid lg:grid-cols-2 gap-8 my-20">
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
            <div class="grid place-items-center">
                <!-- COLLAPSE XPUB -->
                <h1 class="text-2xl font-bold">Don't Trust, Verify!</h1>
                <slot name="extra-description" />

                <h2 class="text-3xl mt-2">&nbsp;</h2>
                
            </div>
        </div>
    </div>    
   
</div>


<div id="anchorId" class="md:flex lg:w-2/3 mx-auto my-12">
    <div class="md:grow">
        {#if onLogin !== null}
            <Login {onLogin} />
        {/if}
        {#if canAddItems || showActiveAuctions || showPastAuctions}
            <h3 class="lg:text-8xl font-bold text-center my-8">Auctions</h3>
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
                    <div slot="new-entity" class="grid lg:grid-cols-2 gap-4" let:setCurrent={setCurrent}>
                        {#if isCampaignStall}
                            <div id="auction-hour-1" class="mx-auto my-10 bg-black w-full grid place-items-center h-64 rounded shadow-xl opacity-80 hover:opacity-100 duration-300 cursor-pointer hover:scale-95" on:click|preventDefault={() => newItem(setCurrent, () => new TimeAuction())}>
                              <p class="lg:text-4xl font-bold text-center text-white">Auction time for 1 hour</p>
                            </div>
                        {/if}
                        <div id="auction-physical" class="mx-auto my-10 bg-black w-full grid place-items-center h-64 rounded shadow-xl opacity-80 hover:opacity-100 duration-300 cursor-pointer hover:scale-95" on:click|preventDefault={() => newItem(setCurrent, () => new Auction())}>
                          <p class="lg:text-4xl font-bold text-center text-white">Auction Item</p>
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
            <h3 class="text-3xl text-center">Fixed price</h3>
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
                        <div id="fixed-price" class="lg:w-1/2 mx-auto my-10 bg-black w-full grid place-items-center h-64 rounded shadow-xl opacity-80 hover:opacity-100 duration-300 cursor-pointer hover:scale-95" on:click|preventDefault={() => newItem(setCurrent, () => new Listing())}>
                          <p class="lg:text-4xl font-bold text-center text-white">Sell Item</p>
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

<div class="pt-6 pb-6">
</div>

<style>
  #auction-hour-1 {
    background-image: url('$lib/images/auction_button1.png');
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
  }

  #auction-physical {
    background-image: url('$lib/images/auction_button2.png');
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
  }

  #fixed-price {
    background-image: url('$lib/images/auction_button2.png');
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
  }
</style>