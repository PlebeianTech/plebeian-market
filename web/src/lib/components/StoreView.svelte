<script lang="ts">
    import PublicAuctionCard from "../components/PublicAuctionCard.svelte";
    import type { Auction } from "../types/auction";
    import type { User } from "../types/user";
    import { type ILoader, getEntities, getStore, getProfile, ErrorHandler } from "../services/api";
    import { onMount } from "svelte";
    import { token, user } from "../stores";
    import StoreNotFound from "./StoreNotFound.svelte";
    import { afterNavigate } from '$app/navigation';
    import type { IEntity } from '$lib/types/base';

    export let storeName;
    export let loader: ILoader;
    export let entities: IEntity[] | null = null;

    let auctions: Auction[] | null = null;
    let store: User;
    let currentTab = "ACTIVE AUCTIONS";
    let loading = true;

    function fetchProfile(tokenValue) {
        getProfile(tokenValue,
            u => {
                user.set(u);
            });
    }

    function fetchStore(storeName: string) {
        getStore(storeName, 
            s => {
                store = s;
                loading = false;
            }, 
            new ErrorHandler(true, () => {
                loading = false
            }));
    }

    function fetchEntities(successCB: () => void = () => {}) {
        getEntities(loader, $token,
            e => {
                entities = e;
                successCB();
            });
    }

    afterNavigate(() => {
        fetchStore(storeName);
        fetchEntities();
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
    {#if store}
        <div class="w-full md:w-1/2 mx-auto mt-4">
            <div class="mx-auto">
                <!-- top profile section -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex-none rounded-full border border-accent avatar lg:h-32 lg:w-32 w-12 h-12 mx-4">
                        <div class="flex justify-center">
                            <img src={store.twitterProfileImageUrl} class="flex-none rounded-full" alt="Avatar"/>
                        </div>
                    </div>
                </div>
                <span class="font-thin text-3xl mx-4">
                    @{store.nym}
                </span>
            </div>
            <div class="flex justify-between md:justify-start md:mx-4 mt-4 mx-8">
                <span class="text-sm font-semibold md:mr-4">{store.activeAuctionCount} Active Auctions</span>
                <span class="text-sm font-semibold">{store.pastAuctionCount} Past Auctions</span>
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
                {#if entities !== null}
                    {#each entities as auction}
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
