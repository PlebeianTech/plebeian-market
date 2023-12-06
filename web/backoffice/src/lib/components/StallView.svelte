<script lang="ts">
    import { onMount } from 'svelte';
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import { postMedia } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { Info,token } from "$sharedLib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";

    let newAuctionsList, activeAuctionsList, pastAuctionsList: ListView;
    let newListingsList, activeListingsList, pastListingsList: ListView;

    function onAuctionSave(key: string, entity: IEntity) {
        user.update((u) => {
            u!.hasItems = true;
            u!.hasOwnItems = true;
            return u;
        });

        let auction = entity as Auction;

        if (auction.added_media.length !== 0) {
            postMedia($token, auction.endpoint, key, auction.added_media, () => onForceReload());
        }

        if (!auction.started) {
            Info.set("Now hit Publish!");
        }

        onForceReload();
    }

    function onListingSave(key: string, entity: IEntity) {
        user.update((u) => {
            u!.hasItems = true;
            u!.hasOwnItems = true;
            return u;
        });

        let listing = entity as Listing;

        if (listing.added_media.length !== 0) {
            postMedia($token, listing.endpoint, key, listing.added_media, () => onForceReload());
        }

        if (!listing.started) {
            Info.set("Now hit Publish!");
        }

        onForceReload();
    }

    function onForceReload() {
        for (let l of [newAuctionsList, activeAuctionsList, pastAuctionsList, newListingsList, activeListingsList, pastListingsList]) {
            if (l) {
                l.fetchEntities();
            }
        }
    }

    onMount(() => window.scrollTo(0, 0));
</script>

<div class="lg:flex lg:w-2/3 mx-auto my-4">
    <div class="w-full px-4">
        <h2 class="text-3xl my-8">Stall Manager</h2>
        <p class="text-center my-4">This is where you list items that you have for sale!</p>
        {#if $user && $user.merchantPublicKey && $user.stallId}
            <p class="text-center my-4">This is the <a class="link" href="{import.meta.env.VITE_BASE_URL}p/{$user.merchantPublicKey}/stall/{$user.stallId}">public link</a> of your stall. You can share this.</p>
        {/if}
        <div class="flex gap-4 flex-col">
            <ListView
                bind:this={newListingsList}
                loader={{endpoint: "users/me/listings?filter=new", responseField: 'listings', fromJson: listingFromJson}}
                postEndpoint={"users/me/listings"}
                onSave={onListingSave}
                {onForceReload}
                editor={ListingEditor}
                card={ItemCard}
                style={ListViewStyle.Grid}>
                <div slot="new-entity" class="flex justify-start" let:setCurrent={setCurrent}>
                    <div class="w-full flex lg:justify-start justify-center">
                        <button class="btn btn-secondary font-bold text-center w-48 my-4" on:click|preventDefault={() => setCurrent(new Listing())}>Fixed price item</button>
                    </div>
                </div>
            </ListView>
            <ListView
                bind:this={newAuctionsList}
                loader={{endpoint: "users/me/auctions?filter=new", responseField: 'auctions', fromJson: auctionFromJson}}
                postEndpoint={"users/me/auctions"}
                onSave={onAuctionSave}
                {onForceReload}
                editor={AuctionEditor}
                card={ItemCard}
                style={ListViewStyle.Grid}>
                <div slot="new-entity" class="lg:flex items-center lg:justify-start justify-center my-4 lg:space-x-4 lg:space-y-0 space-y-2" let:setCurrent={setCurrent}>
                    <div id="anchorIdAuctionItem" class="grid lg:place-items-start place-items-center w-full">
                        <div class="w-full flex lg:justify-start justify-center">
                            <button class="btn btn-secondary font-bold text-center w-48" on:click|preventDefault={() => setCurrent(new Auction())}>Auction item</button>
                        </div>
                    </div>
                </div>
            </ListView>
        </div>

        <ListView
            bind:this={activeListingsList}
            loader={{endpoint: "users/me/listings?filter=active", responseField: 'listings', fromJson: listingFromJson}}
            onSave={onListingSave}
            {onForceReload}
            editor={ListingEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
        <ListView
            bind:this={activeAuctionsList}
            loader={{endpoint: "users/me/auctions?filter=active", responseField: 'auctions', fromJson: auctionFromJson}}
            onSave={onAuctionSave}
            {onForceReload}
            editor={AuctionEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
        <ListView
            bind:this={pastListingsList}
            loader={{endpoint: "users/me/listings?filter=past", responseField: 'listings', fromJson: listingFromJson}}
            onSave={onListingSave}
            {onForceReload}
            editor={ListingEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
        <ListView
            bind:this={pastAuctionsList}
            loader={{endpoint: "users/me/auctions?filter=past", responseField: 'auctions', fromJson: auctionFromJson}}
            onSave={onAuctionSave}
            {onForceReload}
            editor={AuctionEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
    </div>
</div>
