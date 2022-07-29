<script lang="ts">
    import PublicAuctionCard from "../../lib/components/PublicAuctionCard.svelte";
    import type { Auction } from "../../lib/types/auction";
    import { getStoreAuctions, putStoreInfo, getProfile, ErrorHandler } from "../../lib/services/api";
    import { onMount } from "svelte";
    import { token, user, Info } from "../stores";

    export let store;
    let auctions: Auction[] | null = null;
    let currentTab = "ACTIVE AUCTIONS";
    let formDisplay = "hidden";

    function fetchProfile(tokenValue) {
        getProfile(tokenValue,
            u => {
                user.set(u);
            });
    }

    function closeForm() {
        formDisplay = "hidden";
    }

    function toggleForm() {
        formDisplay = formDisplay === "hidden" ? "block" : "hidden";
    }

    function onSubmit() {
        putStoreInfo($token, store.twitterUsername, store.storeName, store.storeDescription, 
            s => {
                store = s;
                Info.set("Your store has been saved!");
                closeForm();
            },
            new ErrorHandler(true, () => {}));
    }

    onMount(async () => {
        fetchProfile($token);
        getStoreAuctions(store.twitterUsername, a => { auctions = a; });
    });
</script>


<div class="pt-16 px-64">
    <!-- top profile section -->
    <div class="flex space-x-12">
        <div class="rounded-full border border-accent-400 avatar h-32 mt-4 ml-12">
            <img src={store.twitterProfileImageUrl} class="w-32 rounded-full" alt="Avatar"/>
        </div>
        <div>
            <div class="flex items-center justify-center">
                <div class="flex space-x-4">
                    <!-- Link to social -->
                    <span class="font-thin text-3xl">
                        @{store.twitterUsername}
                    </span>
                    <!-- if logged in and looking at your store -->
                    {#if $user && $user.twitterUsername === store.twitterUsername }
                    <span class="btn btn-ghost" on:click={toggleForm}>
                        Edit Store
                    </span>
                    {/if}
                </div>
            </div>
            <form on:submit|preventDefault={onSubmit} class="{formDisplay} form-control w-full max-w-xs">
                <label class="label" for="store-name">
                    <span class="label-text">Store Name</span>
                </label>
                <input bind:value="{store.storeName}" type="text" class="input input-bordered w-full max-w-xs" />
                <label class="label" for="store-description">
                    <span class="label-text">Store Description</span>
                </label>
                <input bind:value="{store.storeDescription}" type="text" class="input input-bordered w-full max-w-xs mb-2" />
                <button class="btn" type="submit">Submit</button>
            </form>
            <div class="flex justify-between pt-3">
                <span class="text-sm font-semibold">{store.activeAuctionCount} Active Auctions</span>
                <span class="text-sm font-semibold">{store.pastAuctionCount} Past Auctions</span>
            </div>
            <div class="pt-6 grid">
                <span class="text-2xl semibold">{store.storeName || ""}</span>
                <span class="font-thin">{store.storeDescription || ""}</span>
            </div>
        </div>
    </div>
    <!-- store listing section -->
    <hr class="border-solid border-accent divide-y-0 opacity-50 my-5">
    <div class="tabs flex space-x-4 items-center justify-center">
        {#each ['ACTIVE AUCTIONS', 'PAST AUCTIONS'] as tab}
            <li class="tab tab-bordered text-sm font-semibold" class:tab-active={tab === currentTab} on:click={() => currentTab = tab}>
                <div>{tab}</div>
            </li>
        {/each}
    </div>
</div>
<div class="pt-6 pb-6">
    <div class="grid md:grid-cols-3 grid-cols-1">
        {#if auctions !== null}
            {#each auctions as auction}
                {#if currentTab === 'ACTIVE AUCTIONS' && !auction.ended}
                    <div class="h-auto">
                        <PublicAuctionCard auction={auction} />
                    </div>
                {/if}
                {#if currentTab === 'PAST AUCTIONS' && auction.ended}
                    <div class="h-auto">
                        <PublicAuctionCard auction={auction} />
                    </div>
                {/if}
            {/each}
        {/if}
    </div>
</div>
