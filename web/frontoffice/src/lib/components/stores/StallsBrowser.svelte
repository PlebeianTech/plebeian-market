<script lang="ts">
    import { onMount } from 'svelte';
    import {NostrGlobalConfig, stalls, isSuperAdmin} from "$sharedLib/stores";
    import {formatTimestampNG} from "$sharedLib/nostr/utils.js";
    import Search from "$sharedLib/components/icons/Search.svelte"
    import {refreshStalls} from "$lib/shopping";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import AdminActions from "$lib/components/pagebuilder/AdminActions.svelte";

    export let merchantPubkey: string | null = null;
    export let showStallFilter: boolean = true;

    let sortedStalls = [];
    let filter = null;

    let descriptionLength = 125;

    $: if ($stalls && $stalls.stalls && !$stalls.fetching) {
            if (merchantPubkey) {
                sortedStalls = Object.entries($stalls.stalls)
                    .filter(([, stall]) => {
                        return stall.merchantPubkey === merchantPubkey;
                    })
                    .sort((a, b) => {
                        return b[1].createdAt - a[1].createdAt;
                    });
            } else {
                sortedStalls = Object.entries($stalls.stalls)
                    .sort((a, b) => {
                        return b[1].createdAt - a[1].createdAt;
                    });
            }
    }

    onMount(async () => {
        refreshStalls();
    });
</script>

{#if showStallFilter && !merchantPubkey}
    <div class="flex flex-col sm:flex-row md:my-2 mb-6 sm:mb-3">
        <div class="relative">
            <span class="h-full absolute inset-y-0 left-0 flex items-center pl-2">
                <Search />
            </span>
            <input bind:value={filter} placeholder="Search store title, description or enter a store id"
                   class="block pl-9 pr-4 py-2 w-full md:w-96 rounded border border-gray-400 text-sm focus:outline-none" />
        </div>
    </div>
{/if}

{#if !merchantPubkey || (merchantPubkey && sortedStalls.length !== 0)}
    {#if merchantPubkey}
        <h2 class="font-bold">Market stalls:</h2>
    {/if}

    <div class="relative overflow-x-hidden shadow-md rounded border border-gray-400">
        <div class="bg-gray-100 dark:bg-gray-800 font-sans">
            <main class="container mx-auto p-4">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-8 lg:gap-8 z-[300] mt-2 mb-2">
                    {#each sortedStalls as [stallId, stall]}
                        {#if
                            filter === null ||
                            (
                                filter !== null && (
                                    stall.name?.toLowerCase().includes(filter.toLowerCase()) ||
                                    stall.description?.toLowerCase().includes(filter.toLowerCase()) ||
                                    stall.id?.toLowerCase() === filter.toLowerCase()
                                )
                            )
                        }
                            <div class="bg-white dark:bg-black rounded-lg shadow-md {$isSuperAdmin ? '' : 'hover:scale-110 duration-300'}">
                                <div class="p-4 md:p-6">
                                    <a href="/p/{stall.merchantPubkey}/stall/{stall.id}">
                                        <div class="cursor-pointer">
                                            <div class="float-left h-7 w-7 mr-3"><Store /></div>
                                            <h3 class="text-lg font-semibold">
                                                {#if stall.name}{stall.name}{/if}
                                            </h3>
                                            <p class="mt-2 lg:mt-3 text-gray-600 dark:text-gray-400 {stall.description && stall.description.length > descriptionLength ? 'tooltip tooltip-primary text-left' : ''}" data-tip={stall.description && stall.description.length > descriptionLength ? stall.description : ''}>
                                                {#if stall.description}{stall.description.substring(0,descriptionLength)}{#if stall.description.length > descriptionLength}...{/if}{/if}
                                            </p>
                                            {#if stall.shipping}
                                                <div class="mt-3 text-xs opacity-75">
                                                    <ul>
                                                        {#each stall.shipping as s}
                                                            {#if s.countries}
                                                                <li>{#if s.name}{s.name} - {/if} {s.cost} {stall.currency} - {s.countries?.join(", ")}</li>
                                                            {/if}
                                                        {/each}
                                                    </ul>
                                                </div>
                                            {/if}
                                            {#if stall.createdAt}
                                                <div class="mt-3 text-xs opacity-70">Available since {formatTimestampNG(stall.createdAt)}</div>
                                            {/if}
                                        </div>
                                    </a>
                                    {#if $isSuperAdmin && $NostrGlobalConfig}
                                        <div class="pt-4">
                                            <AdminActions
                                                itemId={stallId}
                                                entityName="stalls"
                                            />
                                        </div>
                                    {/if}
                                </div>
                            </div>
                        {/if}
                    {/each}
                </div>
            </main>
        </div>
    </div>
{/if}
