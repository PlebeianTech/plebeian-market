<script lang="ts">
    import PublicAuctionCard from "../../lib/components/PublicAuctionCard.svelte";
    import type { Auction } from "../../lib/types/auction";
    import { getStore, getStoreAuctions, putStoreInfo, getProfile, ErrorHandler } from "../../lib/services/api";
    import { onMount } from "svelte";
    import { token, user, store, Info } from "../stores";
    import StoreNotFound from "./StoreNotFound.svelte";
    import { afterNavigate } from '$app/navigation';

    export let storeName;
    let auctions: Auction[] | null = null;
    let currentTab = "ACTIVE AUCTIONS";
    let formDisplay = "hidden";
    let loading = true;
    let storeButton = 'Edit Store';

    function fetchProfile(tokenValue) {
        getProfile(tokenValue,
            u => {
                user.set(u);
            });
    }

    function fetchStore(storeName: string) {
        getStore(storeName, 
            s => {
                store.set(s);
                loading = false;
            }, 
            new ErrorHandler(true, () => {
                loading = false
            }));
    }

    function closeForm() {
        formDisplay = "hidden";
    }

    function toggleForm() {
        formDisplay = formDisplay === "hidden" ? "block" : "hidden";
        storeButton = storeButton === "Edit Store" ? "Close Editor" : "Edit Store";
    }

    function onSubmit() {
        storeButton = storeButton === "Edit Store" ? "Close Editor" : "Edit Store";
        putStoreInfo($token, $store.twitterUsername, $store.storeName, $store.storeDescription, 
            s => {
                store.set(s);
                Info.set("Your store has been saved!");
                closeForm();
            },
            new ErrorHandler(true, () => {}));
    }

    afterNavigate(() => {
        fetchStore(storeName);
        getStoreAuctions(storeName, a => { 
            auctions = a;
        });
    });

    onMount(async () => {
        fetchProfile($token);
    });
</script>


{#if loading}
    <div class="hero h-5/6 bg-base-200">
        <div class="hero-content text-center">
            <div class="max-w-md">
                <button class="btn btn-ghost loading btn-lg"></button>
            </div>
        </div>
    </div>
{:else}
    {#if $store}
        <div class="w-full md:w-1/2 mx-auto mt-4">
            <div class="mx-auto">
                <!-- top profile section -->
                <div class="flex items-center justify-between">
                    <div class="flex-none rounded-full border border-accent avatar lg:h-32 lg:w-32 w-12 h-12 mx-4">
                        <div class="flex justify-center">
                            <img src={$store.twitterProfileImageUrl} class="flex-none rounded-full" alt="Avatar"/>
                        </div>
                    </div>
                    <div class="mx-4">
                        <!-- if logged in and looking at your own store -->
                        {#if $user && $user.twitterUsername === $store.twitterUsername }
                        <span class="btn btn-accent" on:click={toggleForm}>
                            {storeButton}
                        </span>
                        {/if}
                    </div>
                </div>
                <span class="font-thin text-3xl mx-4 mt-2">
                    @{$store.twitterUsername}
                </span>
            </div>
            <form on:submit|preventDefault={onSubmit} class="{formDisplay} form-control mx-4 mb-4">
                <label class="label" for="store-name">
                    <span class="label-text">Store Name</span>
                </label>
                <input bind:value={$store.storeName} type="text" class="input input-bordered w-full max-w-xs" maxlength="100"/>
                <label class="label" for="store-description">
                    <span class="label-text">Store Description</span>
                </label>
                <textarea bind:value={$store.storeDescription} rows="6" class="textarea textarea-bordered w-full max-w-xs h-48" maxlength="240"></textarea>
                <button class="btn block mt-2" type="submit">Submit</button>
            </form>
            <div class="flex justify-between md:justify-start md:mx-4 mt-4 mx-8">
                <span class="text-sm font-semibold md:mr-4">{$store.activeAuctionCount} Active Auctions</span>
                <span class="text-sm font-semibold">{$store.pastAuctionCount} Past Auctions</span>
            </div>
            <div class="mt-4 mx-4">
                <div class="text-2xl semibold">{$store.storeName || ""}</div>
                <div class="font-thin">{$store.storeDescription || ""}</div>
            </div>
        </div>
        <!-- store listing section -->
        <hr class="border-solid border-accent divide-y-0 opacity-50 my-5">
        <div class="tabs flex items-center justify-center">
            {#each ['ACTIVE AUCTIONS', 'PAST AUCTIONS'] as tab}
                <li class="tab text-xs font-semibold" class:tab-active={tab === currentTab} class:tab-bordered={tab === currentTab} on:click={() => currentTab = tab}>
                    <div>{tab}</div>
                </li>
            {/each}
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
    {:else}
        <StoreNotFound />
    {/if}
{/if}
