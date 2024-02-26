<script lang="ts">
    import { onMount } from 'svelte';
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import ItemCard from "$lib/components/ItemCard.svelte";
    import ListingEditor from "$lib/components/ListingEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import { postMediaAsync, putPublish } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { token } from "$sharedLib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import { type Item } from "$lib/types/item";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";

    let newAuctionsList, activeAuctionsList, pastAuctionsList: ListView;
    let newListingsList, activeListingsList, pastListingsList: ListView;

    function onProductSaved(key: string, entity: IEntity) {
        user.update((u) => {
            u!.hasItems = true;
            u!.hasOwnItems = true;
            return u;
        });

        let item = entity as unknown as Item;

        let promises: Array<Promise<string>> = [];
        if (item.added_media.length !== 0) {
            for (let addedMedia of item.added_media) {
                promises.push(postMediaAsync($token, item.endpoint, key, addedMedia));
            }
        }

        Promise.all(promises).then(_ => {
            if (item.isPublished()) {
                // re-publish to nostr if the auction was published before editing!
                putPublish($token, item.endpoint, key, onForceReload);
            } else {
                onForceReload();
            }
        });
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

<Titleh1>Stall Manager</Titleh1>

<div class="lg:flex lg:w-2/3 mx-auto my-4">
    <div class="w-full px-4">
        <p class="text-center my-4">This is where you list items that you have for sale!</p>
        {#if $user && $user.merchantPublicKey && $user.stallId}
            <p class="text-center my-4">This is the <a class="link" href="{import.meta.env.VITE_BASE_URL}p/{$user.merchantPublicKey}/stall/{$user.stallId}">public link</a> of your stall. You can share this.</p>
        {/if}
        <div class="flex gap-4 flex-col">
            <ListView
                bind:this={newListingsList}
                loader={{endpoint: "users/me/listings?filter=new", responseField: 'listings', fromJson: listingFromJson}}
                postEndpoint={"users/me/listings"}
                onSave={onProductSaved}
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
                onSave={onProductSaved}
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
            onSave={onProductSaved}
            {onForceReload}
            editor={ListingEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
        <ListView
            bind:this={activeAuctionsList}
            loader={{endpoint: "users/me/auctions?filter=active", responseField: 'auctions', fromJson: auctionFromJson}}
            onSave={onProductSaved}
            {onForceReload}
            editor={AuctionEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
        <ListView
            bind:this={pastListingsList}
            loader={{endpoint: "users/me/listings?filter=past", responseField: 'listings', fromJson: listingFromJson}}
            onSave={onProductSaved}
            {onForceReload}
            editor={ListingEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
        <ListView
            bind:this={pastAuctionsList}
            loader={{endpoint: "users/me/auctions?filter=past", responseField: 'auctions', fromJson: auctionFromJson}}
            onSave={onProductSaved}
            {onForceReload}
            editor={AuctionEditor}
            card={ItemCard}
            style={ListViewStyle.Grid} />
    </div>
</div>
