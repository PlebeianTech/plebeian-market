<script lang="ts">
    import { onMount } from 'svelte';
    import Avatar from "$lib/components/Avatar.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import StallNotFound from "$lib/components/StallNotFound.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import PublicItemCard from "$lib/components/PublicItemCard.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import type { User } from "$lib/types/user";
    import { getProfile, ErrorHandler } from "$lib/services/api";
    import { token, user, Info } from "$lib/stores";
    import { Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";

    export let stallOwnerNym;

    let stallOwner: User;
    let loading = true;

    $: title = stallOwner ? `${stallOwner.nym}'s Stall` : "";
    $: twitterHref = stallOwner && stallOwner.twitter.usernameVerified ? `https://twitter.com/${stallOwner.twitter.username}` : null;

    let AUCTIONS = "Auctions";
    let FIXED_PRICE = "Fixed price";
    let ACTIVE = "Active";
    let PAST = "Past";

    let currentTab: string | null = null;

    $: isMyStall = $user && stallOwner && $user.nym === stallOwner.nym;
    $: tabList = isMyStall ? [AUCTIONS, FIXED_PRICE, ACTIVE, PAST] : [ACTIVE, PAST];

    $: cardType = isMyStall ? ItemCard : PublicItemCard;
    $: showAsGrid = !(isMyStall);

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

    onMount(async () => {
        if (stallOwnerNym !== "") {
            fetchStall(stallOwnerNym);
        }
    });
</script>

{#if loading}
    <Loading />
{:else}
    {#if stallOwner}
        <div class="w-full flex flex-col-reverse md:flex-row mx-auto mt-5">
            <div class="md:grow-0">
                <ul class="menu menu-compact mt-3 bg-base-100 md:w-56 p-2 rounded-box">
                    {#each tabList as tab, i}
                        <li><a class:active={(currentTab === null && i === 0) || (tab === currentTab)} href={null} on:click={() => currentTab = tab}>{tab}</a></li>
                    {/each}
                </ul>
            </div>
            <div class="flex-auto">
                <div class="flex-1 flex flex-row-reverse pr-10">
                    <div>
                        <div class="flex items-center justify-between mb-4">
                            <div class="flex-none lg:h-32 lg:w-32 w-12 h-12 mx-4">
                                <Avatar account={stallOwner.twitter} showUsername={false} height="32" />
                            </div>
                        </div>
                        <div class="flex justify-center items-center font-thin text-3xl mx-4">
                            <a href={twitterHref} class:link={twitterHref !== null} target="_blank">@{stallOwner.nym}</a>
                        </div>
                    </div>
                </div>
                <hr class="w-11/12 mx-auto border-solid border-accent divide-y-0 opacity-50 my-5">
            </div>
        </div>

        <div class="md:flex">
            <div class="md:grow mx-10">
                <div class="h-auto">
                    {#if currentTab === null ? isMyStall : currentTab === AUCTIONS}
                        <ListView
                            title={title}
                            loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=new`, responseField: 'auctions', fromJson: auctionFromJson}}
                            newEntity={() => new Auction()}
                            onCreated={onAuctionCreated}
                            editor={AuctionEditor}
                            showNewButton={true}
                            card={ItemCard}
                            style={ListViewStyle.List} />
                    {:else if currentTab === FIXED_PRICE}
                        <ListView
                            title={title}
                            loader={{endpoint: `users/${stallOwner.nym}/listings?filter=new`, responseField: 'listings', fromJson: listingFromJson}}
                            newEntity={() => new Listing()}
                            onCreated={onListingCreated}
                            editor={ListingEditor}
                            showNewButton={true}
                            card={ItemCard}
                            style={ListViewStyle.List} />
                    {:else if currentTab === null ? !isMyStall : currentTab === ACTIVE}
                        <ListView
                            title={title}
                            loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=running`, responseField: 'auctions', fromJson: auctionFromJson}}
                            editor={null}
                            showNewButton={false}
                            card={cardType}
                            style={showAsGrid ? ListViewStyle.Grid : ListViewStyle.List} />

                        <ListView
                            title={title}
                            loader={{endpoint: `users/${stallOwner.nym}/listings?filter=running`, responseField: 'listings', fromJson: listingFromJson}}
                            editor={ListingEditor}
                            showNewButton={false}
                            card={cardType}
                            style={showAsGrid ? ListViewStyle.Grid : ListViewStyle.List} />
                    {:else if currentTab === PAST}
                        <ListView
                            title={title}
                            loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=ended`, responseField: 'auctions', fromJson: auctionFromJson}}
                            editor={null}
                            showNewButton={false}
                            card={cardType}
                            style={showAsGrid ? ListViewStyle.Grid : ListViewStyle.List} />

                        <ListView
                            title={title}
                            loader={{endpoint: `users/${stallOwner.nym}/listings?filter=ended`, responseField: 'listings', fromJson: listingFromJson}}
                            editor={ListingEditor}
                            showNewButton={false}
                            card={cardType}
                            style={showAsGrid ? ListViewStyle.Grid : ListViewStyle.List} />
                    {/if}
                </div>
            </div>
        </div>

        <div class="pt-6 pb-6">

        </div>
    {:else}
        <StallNotFound />
    {/if}
{/if}
