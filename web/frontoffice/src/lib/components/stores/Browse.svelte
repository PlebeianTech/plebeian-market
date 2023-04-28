<script lang="ts">
    import { onMount } from 'svelte';
    import { NostrPool, stalls } from "$lib/stores";
    import {NostrStall} from "../../types/stall";
    import {formatTimestamp, getFirstTagValue} from "$lib/nostr/utils.js";
    import Search from "$sharedLibComponents/icons/Search.svelte"
    import {refreshStalls} from "../../shopping";

    export let merchantPubkey: string;

    let sortedStalls = [];

    //let merchantMeta = new Map<string, string>();
    let merchantMeta = [];
    let filter = null;

    $: {
        if ($stalls && $stalls.stalls) {
            sortedStalls = Object.entries($stalls.stalls).sort((a, b) => {
                return b[1].createdAt - a[1].createdAt;
            });
        }
    }

    onMount(async () => {
        refreshStalls($NostrPool);
    });
</script>

<div class="relative overflow-x-auto">
    <div class="my-2 flex sm:flex-row flex-col mb-6 sm:mb-3">
         <div class="relative">
            <span class="h-full absolute inset-y-0 left-0 flex items-center pl-2">
                <Search />
            </span>
            <input bind:value={filter} placeholder="Search store title, description or enter a store id"
                   class="appearance-none rounded-r rounded-l sm:rounded-l-none border border-gray-400 border-b block pl-8 pr-4 py-2 w-96
               bg-white focus:bg-white text-sm placeholder-gray-500 text-gray-700 focus:text-gray-700 focus:outline-none" />
        </div>
    </div>

    <div class="relative overflow-x-auto shadow-md sm:rounded-lg">
        <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                <tr>
                    <th scope="col" class="px-6 py-3">Stall Name</th>
                    <th scope="col" class="px-6 py-3">Description</th>
                    <!--<th>By</th>-->
                    <th scope="col" class="px-6 py-3">Currency</th>
                    <th scope="col" class="px-6 py-3">Shipping</th>
                    <th scope="col" class="px-6 py-3 text-center">Since</th>
                </tr>
            </thead>

            <tbody class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                {#each sortedStalls as [stallId, stall]}
                    {#if
                        filter === null ||
                        (
                            filter !== null && (
                                stall.name.toLowerCase().includes(filter.toLowerCase()) ||
                                stall.description.toLowerCase().includes(filter.toLowerCase()) ||
                                stall.id.toLowerCase() === filter.toLowerCase()
                            )
                        )
                    }
                        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover cursor-pointer">
                            <th class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">{#if stall.name}<a href="/p/{stall.merchantPubkey}/stall/{stall.id}">{stall.name}</a>{/if}</th>
                            <td class="px-6 py-4 {stall.description && stall.description.length > 100 ? 'tooltip tooltip-primary' : ''}" data-tip={stall.description && stall.description.length > 100 ? stall.description : ''}>{#if stall.description}{stall.description.substring(0,100)}{#if stall.description.length > 100}...{/if}{/if}</td>
                            <td class="px-6 py-4 text-center">{#if stall.currency}{stall.currency}{/if}</td>
                            <td class="px-6 py-4">
                                {#if stall.shipping}
                                    <ul>
                                    {#each stall.shipping as s}
                                        <li>{s.name} - {s.cost} {s.currency} - {s.countries.join(", ")}</li>
                                    {/each}
                                    </ul>
                                {/if}
                            </td>
                            <th class="px-6 py-4">{#if stall.createdAt}{formatTimestamp(stall.createdAt)}{/if}</th>
                        </tr>
                    {/if}
                {/each}
            </tbody>
        </table>
    </div>
</div>
