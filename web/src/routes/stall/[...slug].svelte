<svelte:head>
    <title>Market Stall</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { stallOwnerNym: slug } }
    }
</script>

<script lang="ts">
    import { onMount } from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';
    import { goto } from "$app/navigation";
    import Avatar from "$lib/components/Avatar.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ItemCardSmall from "$lib/components/ItemCardSmall.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import type { User } from "$lib/types/user";
    import { getProfile, ErrorHandler } from "$lib/services/api";
    import { token, user, Info } from "$lib/stores";
    import { Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";

    export let stallOwnerNym: string;

    let newAuctionsList: ListView, auctionsList: ListView, newListingsList: ListView, listingsList: ListView;

    let stallOwner: User;
    let loading = true;

    $: title = stallOwner ? (stallOwner.stallName !== null ? stallOwner.stallName : `${stallOwner.nym}'s Stall`) : "";
    $: twitterHref = stallOwner ? `https://twitter.com/${stallOwner.twitter.username}` : null;
    $: isMyStall = stallOwner && $user && stallOwner.nym === $user.nym;

    function onAuctionCreated() {
        user.update((u) => { u!.hasItems = true; return u; });
        Info.set("Your auction will start when we verify your tweet!");
    }

    function onListingCreated() {
        user.update((u) => { u!.hasItems = u!.hasListings = true; return u; });
        Info.set("Your listing will become active after we verify your tweet!");
    }

    function fetchStall(stallOwnerNym: string) {
        loading = true;
        getProfile($token, stallOwnerNym,
            s => {
                stallOwner = s;
                loading = false;
            }, 
            new ErrorHandler(false, () => {
                loading = false;
            }));
    }

    function onForceReload() {
        if (isMyStall) {
            for (const l of [newAuctionsList, auctionsList, newListingsList, listingsList]) {
                l.fetchEntities();
            }
        }
    }

    onMount(async () => {
        if (stallOwnerNym === "" || stallOwnerNym === null) {
            goto("/");
        } else {
            fetchStall(stallOwnerNym);
        }
    });
</script>

{#if loading}
    <Loading />
{:else}
    {#if stallOwner}
        <div class="w-2/3 items-center mx-auto">
            <img class="w-full h-64 rounded-md object-cover mt-2" src={stallOwner.stallBannerUrl} alt="" />

            <div class="flex flex-col-reverse md:flex-row mt-4">
                <div class="mt-4 text-center">
                    <Avatar account={stallOwner.twitter} showUsername={false} height="24" />
                </div>

                <div class="ml-4 bg-base-300 rounded flex-1 p-4">
                    <h2 class="text-2xl">{title}</h2>
                    <div class="flex float-right">
                        <span class="mr-4">Contact:</span>
                        <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
                            <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                        </svg>
                        <a href={twitterHref} class:link={twitterHref !== null} target="_blank">@{stallOwner.nym}</a>
                    </div>
                </div>
            </div>
            {#if isMyStall}
                <a href="/settings#onsave=mystall" class="btn btn-xs float-right mt-2">Edit</a>
            {/if}
            {#if stallOwner.stallDescription}
                <div class="markdown-container ml-12 mt-10">
                    <SvelteMarkdown source={stallOwner.stallDescription} />
                </div>
            {/if}
        </div>

        <div class="divider"></div>

        <div class="md:flex">
            <div class="md:grow mx-10">
                {#if isMyStall || stallOwner.hasAuctions}
                    <h3 class="text-3xl">Auctions</h3>
                    {#if isMyStall}
                        <ListView
                            bind:this={newAuctionsList}
                            loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=new`, responseField: 'auctions', fromJson: auctionFromJson}}
                            newEntity={() => new Auction()}
                            onCreated={onAuctionCreated}
                            {onForceReload}
                            editor={AuctionEditor}
                            showNewButton={true}
                            card={ItemCard}
                            style={ListViewStyle.List} />
                    {/if}
                    <ListView
                        bind:this={auctionsList}
                        loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=not-new`, responseField: 'auctions', fromJson: auctionFromJson}}
                        {onForceReload}
                        editor={null}
                        showNewButton={false}
                        card={ItemCardSmall}
                        style={ListViewStyle.Grid} />
                    <div class="divider"></div>
                {/if}
                {#if isMyStall || stallOwner.hasListings}
                    <h3 class="text-3xl">Fixed price</h3>
                    {#if isMyStall}
                        <ListView
                            bind:this={newListingsList}
                            loader={{endpoint: `users/${stallOwner.nym}/listings?filter=new`, responseField: 'listings', fromJson: listingFromJson}}
                            newEntity={() => new Listing()}
                            onCreated={onListingCreated}
                            {onForceReload}
                            editor={ListingEditor}
                            showNewButton={true}
                            card={ItemCard}
                            style={ListViewStyle.List} />
                    {/if}
                    <ListView
                        bind:this={listingsList}
                        loader={{endpoint: `users/${stallOwner.nym}/listings?filter=not-new`, responseField: 'listings', fromJson: listingFromJson}}
                        {onForceReload}
                        editor={isMyStall? ListingEditor : null}
                        showNewButton={false}
                        card={ItemCardSmall}
                        style={ListViewStyle.Grid} />
                {/if}
            </div>
        </div>

        <div class="pt-6 pb-6">

        </div>
    {:else}
        <div class="hero min-h-screen">
            <div class="hero-content text-center">
                <div class="max-w-md">
                    <h1 class="text-5xl font-bold">Stall Not Found</h1>
                    <p class="py-6">The stall you are looking for does not exist</p>
                    <a class="btn btn-primary" href="/">Home</a>
                </div>
            </div>
        </div>
    {/if}
{/if}