<script lang="ts">
    import { onMount } from 'svelte';
    import { NostrPool } from "$lib/stores";
    import {getStalls, subscribeMetadata} from "../../services/nostr";
    import {NostrStall} from "../../types/nip45";
    import {formatTimestamp, getFirstTagValue} from "$lib/nostr/utils.js";

    export let merchant_pubkey: string;

    let stalls: {[stall_id: string]: {}} = {};

    //let merchantMeta = new Map<string, string>();
    let merchantMeta = [];
    let currencies = [];

    let filterCurrency = '';

    function getMerchantMeta() {
        console.log('---------------', merchantMeta);
        if (merchantMeta.length > 0) {
            subscribeMetadata($NostrPool, merchantMeta, (pk, m) => {
                //merchantMeta.set(pk, m);
                console.log('*************  pk', pk);
                console.log('*************  m', m);
            });
        }
    }

    function openStore(merchantPubkey, stall_id) {
        window.location.href = "/p/"+merchantPubkey+"/stall/"+stall_id;
    }

    onMount(async () => {
        getStalls($NostrPool, merchant_pubkey,
            (stallEvent) => {
                let content = JSON.parse(stallEvent.content)
                content.createdAt = stallEvent.created_at;
                content.merchantPubkey = stallEvent.pubkey;

                /*
                if (!merchantMeta.has(stallEvent.pubkey)) {
                    merchantMeta.set(stallEvent.pubkey, null);
                }*/
                if (!merchantMeta.includes(stallEvent.pubkey)) {
                    merchantMeta.push(stallEvent.pubkey);
                }

                if (!currencies.includes(content.currency)) {
                    currencies.push(content.currency);
                    currencies = currencies;
                }

                //console.log('******************** STORE '+content.merchantPubkey+' ********************', stallEvent);

                if (!content.id) {
                    let stall_id = getFirstTagValue(stallEvent.tags, 'd');
                    if (stall_id !== null) {
                        content.id = stall_id;
                    } else {
                        return;
                    }
                }

                let stall_id = content.id;

                if (stall_id in stalls) {
                    if (stalls[stall_id].createdAt < stallEvent.created_at) {
                        stalls[stall_id] = content;
                    }
                } else {
                    stalls[stall_id] = content;
                }
            });

        // setTimeout(getMerchantMeta, 4000);
    });
</script>

<div class="relative overflow-x-auto">
    <div class="my-2 flex sm:flex-row flex-col mb-2 sm:mb-1">
        <div class="relative">
            <select
                    bind:value={filterCurrency}
                    class="appearance-none h-full rounded-l border block appearance-none w-full bg-white border-gray-400 text-gray-700 py-2 px-4 pr-8 leading-tight focus:outline-none focus:bg-white focus:border-gray-500">
                <option value="">All currencies</option>
                {#each currencies as currency}
                    <option value="{currency}">{currency}</option>
                {/each}
            </select>
            <div
                    class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
            </div>
        </div>
        <!--
        <div class="relative">
            <select
                    class="appearance-none h-full rounded-r border-t sm:rounded-r-none sm:border-r-0 border-r border-b block appearance-none w-full bg-white border-gray-400 text-gray-700 py-2 px-4 pr-8 leading-tight focus:outline-none focus:border-l focus:border-r focus:bg-white focus:border-gray-500">
                <option>All</option>
                <option>Active</option>
                <option>Inactive</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
            </div>
        </div>
        -->
        <div class="relative">
            <span class="h-full absolute inset-y-0 left-0 flex items-center pl-2">
                <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current text-gray-500">
                    <path d="M10 4a6 6 0 100 12 6 6 0 000-12zm-8 6a8 8 0 1114.32 4.906l5.387 5.387a1 1 0 01-1.414 1.414l-5.387-5.387A8 8 0 012 10z"></path>
                </svg>
            </span>
            <input placeholder="Search store title, description or enter a store id"
                   class="appearance-none rounded-r rounded-l sm:rounded-l-none border border-gray-400 border-b block pl-8 pr-4 py-2 w-96
               bg-white focus:bg-white text-sm placeholder-gray-500 text-gray-700 focus:text-gray-700 focus:outline-none" />
        </div>
    </div>

    <table class="table table-auto table-zebra w-full">
        <thead>
            <tr>
                <th>Shop Name</th>
                <th>Description</th>
                <!--<th>By</th>-->
                <th>Currency</th>
                <th>Shipping</th>
                <th class="text-center">Since</th>
            </tr>
        </thead>

        <tbody>
            {#each Object.entries(stalls) as [stall_id, stall]}
                {#if filterCurrency === '' || (filterCurrency !== '' && filterCurrency === stall.currency)}
                    <tr class="hover cursor-pointer" on:click={() => openStore(stall.merchantPubkey, stall.id)()}>
                        <td>{#if stall.name}<a href="/p/{stall.merchantPubkey}/stall/{stall.id}">{stall.name}</a>{/if}</td>
                        <td class="{stall.description && stall.description.length > 100 ? 'tooltip tooltip-primary' : ''}" data-tip={stall.description && stall.description.length > 100 ? stall.description : ''}>{#if stall.description}{stall.description.substring(0,100)}{#if stall.description.length > 100}...{/if}{/if}</td>
                        <td class="text-center">{#if stall.currency}{stall.currency}{/if}</td>
                        <td>
                            {#if stall.shipping}
                                <ul>
                                {#each stall.shipping as s}
                                    <li>{s.name} - {s.cost} {s.currency} - {s.countries.join(", ")}</li>
                                {/each}
                                </ul>
                            {/if}
                        </td>
                        <td>{#if stall.createdAt}{formatTimestamp(stall.createdAt)}{/if}</td>
                    </tr>
                {/if}
            {/each}
        </tbody>
    </table>
</div>
