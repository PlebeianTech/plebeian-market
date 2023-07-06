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
    import {newNostrConversation} from "$lib/nostr/utils";
    import {getConfigurationFromFile} from "$lib/utils";

    export let merchantPubkey: string;

    let isSuperAdmin: boolean = false;

    let sortedStalls = [];
    let filter = null;

    $: {
        if ($stalls && $stalls.stalls) {
            if (merchantPubkey) {
                sortedStalls = Object.entries($stalls.stalls)
                    .filter(([, stall]) => {
                        return stall.merchantPubkey === merchantPubkey;
                    })
                    .sort((a, b) => {
                        return b[1].createdAt - a[1].createdAt;
                    });
            } else {
                sortedStalls = Object.entries($stalls.stalls).sort((a, b) => {
                    return b[1].createdAt - a[1].createdAt;
                });
            }
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

        let config = await getConfigurationFromFile();
        if (config && config.admin_pubkey.length === 64 && $NostrPublicKey === config.admin_pubkey) {
            isSuperAdmin = true;
        }
    });
</script>

{#if !merchantPubkey}
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

{#if merchantPubkey && sortedStalls.length === 0}
    {#if merchantPubkey === $NostrPublicKey}
        <div class="alert alert-warning shadow-lg">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                <span>You don't have a market stall yet. Start by <a href="/admin" class="underline">creating one</a>.</span>
            </div>
        </div>
    {:else}
        <div class="alert alert-info shadow-lg mb-8 md:mb-12">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span>This Nostr user doesn't have a market stall yet. You can <a class="underline" href="/stalls">explore other market stalls</a> or
                    <a class="underline cursor-pointer" on:click={() => newNostrConversation(merchantPubkey)}>contact with the user</a>.
                </span>
            </div>
        </div>
    {/if}
{/if}

{#if !merchantPubkey || (merchantPubkey && sortedStalls.length !== 0)}
    {#if merchantPubkey}
        <h2>
            <b>Market stalls:</b>
        </h2>
    {/if}

    <div class="relative overflow-x-hidden shadow-md rounded border border-gray-400">
        <!-- Desktop -->
        <table class="hidden md:block w-full text-sm text-left">
            <thead class="text-xs uppercase">
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

            <tbody>
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
                        <tr class="border-y border-gray-400 hover cursor-pointer">
                            <th class="px-6 py-4 font-medium whitespace-nowrap" on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>{#if stall.name}{stall.name}{/if}</th>
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
                                {#if !$NostrGlobalConfig.homepage_sections}
                                    {#if $NostrGlobalConfig.homepage_include_stalls && $NostrGlobalConfig.homepage_include_stalls.includes(stall.id)}
                                        <div class="tooltip tooltip-primary tooltip-left" data-tip="Remove products from the Homepage">
                                            <button class="btn btn-s btn-circle btn-ghost" on:click|preventDefault={() => removeStallFromHomePage(stall.id)}><span class="w-6 text-rose-500"><Minus /></span></button>
                                        </div>
                                    {:else}
                                        <div class="tooltip tooltip-primary tooltip-left" data-tip="Add products to the Homepage">
                                            <button class="btn btn-s btn-circle btn-ghost" on:click|preventDefault={() => addStallToHomePage(stall.id)}><span class="w-6 text-green-500"><Plus /></span></button>
                                        </div>
                                    {/if}
                                {:else}
                                    <div class="dropdown dropdown-left">
                                        <div tabindex="0" class="tooltip tooltip-primary tooltip-top" data-tip="Add products">
                                            <button class="btn btn-s btn-circle btn-ghost"><span class="w-6 text-green-500"><Plus /></span></button>
                                        </div>
                                        <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-300 rounded-box w-52">
                                            {#each $NostrGlobalConfig.homepage_sections as section}
                                                <li><a>{section.title}</a></li>
                                            {/each}
                                        </ul>
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
        <table class="md:hidden w-full text-left">
            <tbody>
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
                        <tr class="border-b border-gray-400 cursor-pointer" on:click={() => goto('/p/'+stall.merchantPubkey+'/stall/'+stall.id)}>
                            <th class="p-4 font-medium">
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
{/if}
