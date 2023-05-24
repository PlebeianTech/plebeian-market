<script lang="ts">
    import { onMount } from 'svelte';
    import {NostrGlobalConfig, NostrPublicKey, stalls} from "$lib/stores";
    import {formatTimestamp} from "$lib/nostr/utils.js";
    import Search from "$sharedLib/components/icons/Search.svelte"
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import Minus from "$sharedLib/components/icons/Minus.svelte";
    import {refreshStalls} from "$lib/shopping";
    import { goto } from "$app/navigation";
    import {publishConfiguration} from "$lib/services/nostr";

    export let merchantPubkey: string;

    let isSuperAdmin: boolean = false;

    let sortedStalls = [];
    let filter = null;

    $: {
        if ($stalls && $stalls.stalls) {
            sortedStalls = Object.entries($stalls.stalls).sort((a, b) => {
                return b[1].createdAt - a[1].createdAt;
            });
        }
    }

    function addStallToHomePage(stall_id) {
        let configChanged = false;

        if (Array.isArray($NostrGlobalConfig.homepage_include_stalls)) {
            if (!$NostrGlobalConfig.homepage_include_stalls.includes(stall_id)) {
                $NostrGlobalConfig.homepage_include_stalls.push(stall_id);
                configChanged = true;
            }
        } else {
            $NostrGlobalConfig.homepage_include_stalls = [stall_id];
            configChanged = true;
        }

        console.log('addStallToHomePage - $NostrGlobalConfig. Pushing to relays...', $NostrGlobalConfig);

        if (configChanged) {
            publishConfiguration($NostrGlobalConfig,
                () => {
                    console.log('Configuration saved to Nostr relay!!');
                });
        }
    }

    function removeStallFromHomePage(stall_id) {
        $NostrGlobalConfig.homepage_include_stalls = $NostrGlobalConfig.homepage_include_stalls.filter(object => {
            return object !== stall_id;
        });

        console.log('removeStallFromHomePage - $NostrGlobalConfig. Pushing to relays...', $NostrGlobalConfig);

        publishConfiguration($NostrGlobalConfig,
            () => {
                console.log('Configuration saved to Nostr relay!!');
            });
    }

    onMount(async () => {
        refreshStalls();

        let response = await fetch('config.json')
        let config = await response.json();

        if (config && config.admin_pubkey.length === 64 && $NostrPublicKey === config.admin_pubkey) {
            isSuperAdmin = true;
        }
    });
</script>

<div class="flex flex-col sm:flex-row md:my-2 mb-6 sm:mb-3">
     <div class="relative">
        <span class="h-full absolute inset-y-0 left-0 flex items-center pl-2">
            <Search />
        </span>
        <input bind:value={filter} placeholder="Search store title, description or enter a store id"
               class="block pl-9 pr-4 py-2 w-full md:w-96 appearance-none rounded-r rounded-l sm:rounded-l-none border border-gray-400 border-b
               bg-white focus:bg-white text-sm text-gray-700 focus:text-gray-700 placeholder-gray-500 focus:outline-none" />
    </div>
</div>

<div class="relative overflow-x-auto shadow-md sm:rounded-lg">
    <!-- Desktop -->
    <table class="hidden md:block table-auto w-full text-sm text-left text-gray-500 dark:text-gray-400">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
                <th scope="col" class="px-6 py-3">Stall Name</th>
                <th scope="col" class="px-6 py-3">Description</th>
                <th scope="col" class="px-6 py-3">Currency</th>
                <th scope="col" class="px-6 py-3">Shipping</th>
                <th scope="col" class="px-6 py-3 text-center">Since</th>
                {#if isSuperAdmin}
                    <th scope="col" class="px-6 py-3 text-center">Admin actions</th>
                {/if}
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
                        <th class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white" on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>{#if stall.name}{stall.name}{/if}</th>
                        <td class="px-6 py-4 text-left {stall.description && stall.description.length > 100 ? 'tooltip tooltip-primary' : ''}" data-tip={stall.description && stall.description.length > 100 ? stall.description : ''} on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>{#if stall.description}{stall.description.substring(0,100)}{#if stall.description.length > 100}...{/if}{/if}</td>
                        <td class="px-6 py-4 text-center" on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>{#if stall.currency}{stall.currency}{/if}</td>
                        <td class="px-6 py-4" on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>
                            {#if stall.shipping}
                                <ul>
                                {#each stall.shipping as s}
                                    <li>
                                        {#if s.name}{s.name} - {/if}{s.cost} {stall.currency} - {s.countries.join(", ")}
                                    </li>
                                {/each}
                                </ul>
                            {/if}
                        </td>
                        <td class="px-6 py-4" on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>
                            <p class="mr-1">
                                {#if stall.createdAt}{formatTimestamp(stall.createdAt)}{/if}
                            </p>
                        </td>
                        {#if isSuperAdmin}
                            <th scope="col" class="px-6 py-3 text-center">
                                {#if !$NostrGlobalConfig.homepage_include_stalls.includes(stall.id)}
                                    <div class="tooltip tooltip-primary tooltip-left" data-tip="Add products to Homepage">
                                        <button class="btn btn-s btn-circle btn-ghost" on:click|preventDefault={() => addStallToHomePage(stall.id)}><span class="w-6 text-green-500"><Plus /></span></button>
                                    </div>
                                {/if}
                                {#if $NostrGlobalConfig.homepage_include_stalls.includes(stall.id)}
                                    <div class="tooltip tooltip-primary tooltip-left" data-tip="Products included in Homepage. Remove.">
                                        <button class="btn btn-s btn-circle btn-ghost" on:click|preventDefault={() => removeStallFromHomePage(stall.id)}><span class="w-6 text-rose-500"><Minus /></span></button>
                                    </div>
                                {/if}
                            </th>
                        {/if}
                    </tr>
                {/if}
            {/each}
        </tbody>
    </table>

    <!-- Mobile -->
    <table class="md:hidden text-left text-gray-500 dark:text-gray-400">
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
                    <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover" on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>
                        <th class="p-4 font-medium text-gray-900 dark:text-white">
                            <div>
                                <div class="font-bold">{#if stall.name}{stall.name}{/if}</div>
                                <div class="text-sm opacity-50">{#if stall.description}{stall.description.substring(0,100)}{#if stall.description.length > 100}...{/if}{/if}</div>
                                {#if stall.createdAt}
                                    <div class="mt-1 text-xs opacity-50">Since {formatTimestamp(stall.createdAt)}</div>
                                {/if}
                                <div class="mt-1 text-xs opacity-50">
                                    {#if stall.shipping}
                                        <ul>
                                            {#each stall.shipping as s}
                                                <li>{#if s.name}{s.name} - {/if} {s.cost} {stall.currency} - {s.countries.join(", ")}</li>
                                            {/each}
                                        </ul>
                                    {/if}
                                </div>
                            </div>
                        </th>
                    </tr>
                {/if}
            {/each}
        </tbody>
    </table>
</div>
