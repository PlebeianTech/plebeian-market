<script lang="ts">
    import { onMount } from 'svelte';
    import {NostrGlobalConfig} from "$lib/stores";
    import {NostrPublicKey, stalls} from "$sharedLib/stores";
    import {formatTimestamp} from "$sharedLib/nostr/utils.js";
    import Search from "$sharedLib/components/icons/Search.svelte"
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import Minus from "$sharedLib/components/icons/Minus.svelte";
    import {refreshStalls} from "$lib/shopping";
    import { goto } from "$app/navigation";
    import {publishConfiguration} from "$sharedLib/services/nostr";
    import {newNostrConversation} from "$sharedLib/nostr/utils";
    import {getConfigurationFromFile} from "$sharedLib/utils";
    import InfoBox from "$sharedLib/components/notifications/InfoBox.svelte";

    export let merchantPubkey: string | null;
    export let showStallFilter: boolean = true;

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
                sortedStalls = Object.entries($stalls.stalls)
                    .sort((a, b) => {
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
        if (config && config.admin_pubkeys.includes($NostrPublicKey)) {
            isSuperAdmin = true;
        }
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

{#if merchantPubkey && sortedStalls.length === 0}
    {#if merchantPubkey === $NostrPublicKey}
        <InfoBox classText="mx-auto mt-3">
            <b>You don't have a market stall</b> yet.<br />
            If you want to create one to <b>sell</b> or <b>auction</b> your products, login to the <a rel="external" href="/admin" class="underline"><b>Stall manager</b></a>.
        </InfoBox>
    {:else}
        <InfoBox classText="mb-8 md:mb-12">
            This Nostr user doesn't have a market stall yet. You can <a class="underline" href="/stalls">explore other market stalls</a> or
            <a class="underline cursor-pointer" on:click={() => newNostrConversation(merchantPubkey)}>contact with the user</a>.
        </InfoBox>
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
        <table class="hidden md:block w-full text-sm text-left pb-32">
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
                                                {#if s.name}{s.name} - {/if}{s.cost} {stall.currency} - {s.countries?.join(", ")}
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
                                            <ul tabindex="0" class="dropdown-content menu shadow bg-base-300 rounded-box w-52 rounded border border-gray-400">
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
                                                    <li>{#if s.name}{s.name} - {/if} {s.cost} {stall.currency} - {s.countries?.join(", ")}</li>
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
