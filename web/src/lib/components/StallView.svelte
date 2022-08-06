<script lang="ts">
    import PublicAuctionCard from "../components/PublicAuctionCard.svelte";
    import type { User } from "../types/user";
    import { type ILoader, getEntities, getStall, getProfile, ErrorHandler } from "../services/api";
    import { onMount } from "svelte";
    import { token, user } from "../stores";
    import StallNotFound from "./StallNotFound.svelte";
    import { afterNavigate } from '$app/navigation';
    import type { IEntity } from '$lib/types/base';
    import MetaTags from "./MetaTags.svelte";

    export let stallName;
    export let loader: ILoader;
    export let entities: IEntity[] | null = null;

    let title = `${stallName}'s Market Stall`;
    let stallOwner: User;
    let currentTab = "ACTIVE AUCTIONS";
    let loading = true;

    function fetchProfile(tokenValue) {
        getProfile(tokenValue,
            u => {
                user.set(u);
            });
    }

    function fetchStall(stallName: string) {
        getStall(stallName, 
            s => {
                stallOwner = s;
                loading = false;
            }, 
            new ErrorHandler(true, () => {
                loading = false;
            }));
    }

    function fetchEntities() {
        getEntities(loader, $token,
            e => {
                entities = e;
            });
    }

    afterNavigate(() => {
        fetchStall(stallName);
        fetchEntities();
    });

    onMount(async () => {
        fetchProfile($token);
    });
</script>


<svelte:head>
    <MetaTags {title} />
</svelte:head>

{#if loading}
    <div class="hero h-5/6 bg-base-200">
        <div class="hero-content text-center">
            <div class="max-w-md">
                <div class="lds-ring"><div></div><div></div><div></div><div></div></div>
            </div>
        </div>
    </div>
{:else}
    {#if stallOwner}
        <div class="w-full md:w-1/2 mx-auto mt-4">
            <div class="mx-auto">
                <!-- top profile section -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex-none rounded-full border border-accent avatar lg:h-32 lg:w-32 w-12 h-12 mx-4">
                        <div class="flex justify-center">
                            <img src={stallOwner.twitter.profileImageUrl} class="flex-none rounded-full" alt="Avatar"/>
                        </div>
                    </div>
                </div>
                <span class="font-thin text-3xl mx-4">
                    @{stallOwner.nym}
                </span>
                {#if entities === null || entities.length === 0}
                    <div class="mt-4 mx-4 font-thin text-xl mb-4">
                        User is not selling anything
                    </div>
                {:else}
                    <div class="flex justify-between md:justify-start md:mx-4 mt-4 mx-8">
                        <span class="text-sm font-semibold md:mr-4">{stallOwner.runningAuctionCount} Active Auctions</span>
                        <span class="text-sm font-semibold">{stallOwner.endedAuctionCount} Past Auctions</span>
                    </div>
                {/if}
            </div>
        </div>
        {#if entities !== null && entities.length > 0}
        <!-- stallOwner listing section -->
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
            </div>
        </div>
        {/if}
    {:else}
        <StallNotFound />
    {/if}
{/if}
