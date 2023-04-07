<script lang="ts">
    import { onMount } from 'svelte';
    import { NostrPool } from "$lib/stores";
    import {getStalls, subscribeMetadata} from "../../services/nostr";
    import {NostrStall} from "../../types/stall";
    import {formatTimestamp, getFirstTagValue} from "$lib/nostr/utils.js";

    export let merchantPubkey: string;

    let stalls: {[stallId: string]: {}} = {};

    //let merchantMeta = new Map<string, string>();
    let merchantMeta = [];
    let filter = null;

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

    onMount(async () => {
        getStalls($NostrPool, merchantPubkey,
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

                /*
                if (!currencies.includes(content.currency)) {
                    currencies.push(content.currency);
                    currencies = currencies;
                }
                */

                //console.log('******************** STORE '+content.merchantPubkey+' ********************', stallEvent);

                if (!content.id) {
                    let stallId = getFirstTagValue(stallEvent.tags, 'd');
                    if (stallId !== null) {
                        content.id = stallId;
                    } else {
                        return;
                    }
                }

                let stallId = content.id;

                if (stallId in stalls) {
                    if (stalls[stallId].createdAt < stallEvent.created_at) {
                        stalls[stallId] = content;
                    }
                } else {
                    stalls[stallId] = content;
                }
            });

        // setTimeout(getMerchantMeta, 4000);
    });
</script>

<div class="relative overflow-x-auto">
    <div class="my-2 flex sm:flex-row flex-col mb-6 sm:mb-3">
        <div class="relative">
            <div
                    class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                </svg>
            </div>
        </div>
         <div class="relative">
            <span class="h-full absolute inset-y-0 left-0 flex items-center pl-2">
                <svg viewBox="0 0 24 24" class="h-5 w-5 fill-current text-gray-500">
                    <path d="M10 4a6 6 0 100 12 6 6 0 000-12zm-8 6a8 8 0 1114.32 4.906l5.387 5.387a1 1 0 01-1.414 1.414l-5.387-5.387A8 8 0 012 10z"></path>
                </svg>
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
                {#each Object.entries(stalls) as [stallId, stall]}
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
