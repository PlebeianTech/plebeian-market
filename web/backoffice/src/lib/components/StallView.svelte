<script lang="ts">
    import { goto } from "$app/navigation";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import { putPublish, postMedia } from "$lib/services/api";
    import { Info, user } from "$lib/stores";
    import { token } from "$sharedLib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import type { IAccount } from "$lib/types/user";
    import { Category } from '$lib/types/item';

    export let baseUrl: string;

    export let owner: IAccount | null;
    export let title: string | null;
    export let description: string | null;

    export let isOwnStall = false;

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
</script>

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
                        <div id="anchorIdAuctionItem" class="grid lg:place-items-start place-items-center w-full">
                            <div class="w-full flex lg:justify-start justify-center">
                                <button class="btn btn-secondary font-bold text-center w-48" on:click|preventDefault={() => setCurrent(new Auction())}>Auction Item</button>
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
                            <button class="btn btn-secondary font-bold text-center w-48 my-4" on:click|preventDefault={() => setCurrent(new Listing())}>Sell Item</button>
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
