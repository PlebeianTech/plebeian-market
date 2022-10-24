<script lang="ts">
    import SvelteMarkdown from 'svelte-markdown';
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import Avatar from "$lib/components/Avatar.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ItemCardSmall from "$lib/components/ItemCardSmall.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import { user, Info } from "$lib/stores";
    import { Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import type { IAccount } from "$lib/types/user";

    export let baseUrl: string;

    export let bannerUrl: string | null;
    export let owner: IAccount | null;
    export let title: string;
    export let description: string | null;
    export let onEdit: (() => void) | null = null;

    export let showItemsOwner: boolean;
    export let showItemsCampaign: boolean;
    export let canAddItems: boolean;
    export let hasAuctions: boolean;
    export let hasListings: boolean;

    let newAuctionsList: ListView, auctionsList: ListView, newListingsList: ListView, listingsList: ListView;

    $: twitterUsername = owner ? owner.twitterUsername : null;
    $: twitterHref = owner ? `https://twitter.com/${owner.twitterUsername}` : null;

    function onAuctionCreated() {
        user.update((u) => { u!.hasItems = u!.hasAuctions = true; return u; });
        Info.set("Your auction will start when we verify your tweet!");
    }

    function onListingCreated() {
        user.update((u) => { u!.hasItems = u!.hasListings = true; return u; });
        Info.set("Your listing will become active after we verify your tweet!");
    }

    function onForceReload() {
        if (canAddItems) {
            for (const l of [newAuctionsList, auctionsList, newListingsList, listingsList]) {
                l.fetchEntities();
            }
        }
    }
</script>

<div class="w-11/12 md:w-2/3 items-center mx-auto mt-2">
    <!-- always keep a 3:1 aspect ratio, see https://stackoverflow.com/a/12121309 -->
    <div class="w-full inline-block relative after:pt-[33.33%] after:block after:content-['']">
        <div class="absolute top-0 bottom-0 left-0 right-0 rounded-md bg-center bg-no-repeat bg-cover" style="background-image: url({bannerUrl});" alt=""></div>
    </div>

    <div class="flex flex-col-reverse md:flex-row mt-4">
        <div class="mt-4 text-center">
            {#if owner}
                <Avatar account={owner} height="24" />
            {/if}
        </div>

        <div class="md:ml-4 ml-0 bg-base-300 rounded flex-1 p-4">
            <h2 class="text-2xl">{title}</h2>
            <div class="flex float-right">
                <span class="mr-4">Contact:</span>
                <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
                    <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                </svg>
                {#if twitterHref}
                    <a href={twitterHref} class:link={twitterHref !== null} target="_blank">@{twitterUsername}</a>
                {/if}
            </div>
        </div>
    </div>
    {#if onEdit}
        <a href={null} on:click={onEdit} class="btn btn-xs float-right mt-2">Edit</a>
    {/if}
    {#if description}
        <div class="markdown-container ml-0 md:ml-12 mt-10">
            <SvelteMarkdown source={description} />
        </div>
    {/if}
</div>

<div class="divider"></div>

<div class="md:flex">
    <div class="md:grow mx-10">
        {#if canAddItems || hasAuctions}
            <h3 class="text-3xl">Auctions</h3>
            {#if canAddItems}
                <ListView
                    bind:this={newAuctionsList}
                    loader={{endpoint: `${baseUrl}/auctions?filter=new`, responseField: 'auctions', fromJson: auctionFromJson}}
                    postEndpoint={`${baseUrl}/auctions`}
                    newEntity={() => new Auction()}
                    onCreated={onAuctionCreated}
                    {onForceReload}
                    editor={AuctionEditor}
                    {showItemsOwner} {showItemsCampaign}
                    showNewButton={true}
                    card={ItemCard}
                    style={ListViewStyle.List} />
            {/if}
            <ListView
                bind:this={auctionsList}
                loader={{endpoint: `${baseUrl}/auctions?filter=not-new`, responseField: 'auctions', fromJson: auctionFromJson}}
                {onForceReload}
                editor={null}
                {showItemsOwner} {showItemsCampaign}
                showNewButton={false}
                card={ItemCardSmall}
                style={ListViewStyle.Grid} />
            <div class="divider"></div>
        {/if}
        {#if canAddItems || hasListings}
            <h3 class="text-3xl">Fixed price</h3>
            {#if canAddItems}
                <ListView
                    bind:this={newListingsList}
                    loader={{endpoint: `${baseUrl}/listings?filter=new`, responseField: 'listings', fromJson: listingFromJson}}
                    postEndpoint={`${baseUrl}/listings`}
                    newEntity={() => new Listing()}
                    onCreated={onListingCreated}
                    {onForceReload}
                    editor={ListingEditor}
                    {showItemsOwner} {showItemsCampaign}
                    showNewButton={true}
                    card={ItemCard}
                    style={ListViewStyle.List} />
            {/if}
            <ListView
                bind:this={listingsList}
                loader={{endpoint: `${baseUrl}/listings?filter=not-new`, responseField: 'listings', fromJson: listingFromJson}}
                {onForceReload}
                editor={canAddItems ? ListingEditor : null}
                {showItemsOwner} {showItemsCampaign}
                showNewButton={false}
                card={ItemCardSmall}
                style={ListViewStyle.Grid} />
        {/if}
    </div>
</div>

<div class="pt-6 pb-6">
</div>