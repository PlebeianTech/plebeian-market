<script lang="ts">
    import ProductList from "$lib/components/stores/ProductList.svelte";
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import Expand from "$sharedLibComponents/icons/Expand.svelte";
    import Contract from "$sharedLibComponents/icons/Contract.svelte";
    import Store from "$sharedLibComponents/icons/Store.svelte";
    import {onMount} from "svelte";
    import {NostrPool, stalls} from "$lib/stores";
    import {getStallsByMerchant, refreshStalls} from "$lib/shopping";
    import {getChannelIdForStall} from "$lib/nostr/utils";
    import { goto } from '$app/navigation';

    /** @type {import('./$types').PageData} */
    export let data;
    export let pubkey;

    let nostrRoomId: string | null = getChannelIdForStall(data.stallId) ?? null;
    let bigChat: boolean = false;
    let merchantStalls = [];

    let showStallsByMerchantModal = false;

    $: numStallsThisMerchant = Object.keys(merchantStalls ?? []).length ?? 0;

    $: {
        if (data.pubkey && $stalls?.stalls[data.stallId]) {
            merchantStalls = getStallsByMerchant(data.pubkey);
        }
    }

    onMount(async () => {
        refreshStalls($NostrPool);
    });

    function gotoStall(url) {
        goto('/messages')
    }
</script>

<svelte:head>
    <title>Product Browser</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-8 mb-0 p-4">
    {#if $stalls !== null && $stalls.stalls[data.stallId]}
        {$stalls.stalls[data.stallId].name}
    {:else}
        Products in the store
    {/if}
</h1>

{#if numStallsThisMerchant > 1}
    <div class="text-center text-sm mb-8">
        This merchant has {numStallsThisMerchant} stores. Visit them <a on:click|preventDefault={() => showStallsByMerchantModal = true} class="underline decoration-indigo-500 hover:decoration-2 hover:font-bold">here</a>.
    </div>
{/if}

<div class="flex flex-row md:columns-2">
    <div class="{bigChat ? 'lg:basis-2/4' : 'lg:basis-3/4'}  lg:overflow-y-hidden my-2 grid place-items-top top-20 lg:px-0 px-2">
        <div class="grid justify-center items-center lg:mx-20 gap-6 place-content-center">
            <ProductList merchantPubkey={data.pubkey} stallId={data.stallId}></ProductList>
        </div>
    </div>

    {#if nostrRoomId !== null}
        <div class="{bigChat ? 'lg:basis-2/4' : 'lg:basis-1/4'} max-h-screen overflow-y-auto lg:overflow-y-hidden my-2 grid place-items-top top-20 lg:px-0 px-2">
            <h3 class="text-2xl lg:text-3xl fontbold mt-0 lg:mt-2 text-center">Stall Chat</h3>

            <div class="btn-group float-right text-center">
                <button class="btn btn-secondary" class:btn-active={bigChat} on:click={() => bigChat = !bigChat}>
                    {#if bigChat}
                        <div class="w-6"><Contract /></div>
                    {:else}
                        <div class="w-6"><Expand /></div>
                    {/if}
                </button>
            </div>

            <NostrChat
                    messageLimit={500}
                    {nostrRoomId} />
        </div>
    {/if}
</div>

<input type="checkbox" id="stallsByThisMerchant" class="modal-toggle" bind:checked={showStallsByMerchantModal}/>
<div class="modal">
    <div class="modal-box relative">
        <label for="stallsByThisMerchant" class="btn btn-sm btn-circle absolute right-2 top-2">✕</label>
        <div class="w-8 h-8">
            <Store />
        </div>
        <h3 class="text-lg font-bold">Stores by the same merchant:</h3>

        <ul class="list-disc list-inside">
            {#each Object.entries(merchantStalls) as [stallId, stall]}
                <li class="mt-4 ml-4">
                    <a class="underline hover:decoration-2 hover:font-bold" href="/p/{stall.merchantPubkey}/stall/{stallId}" on:click={() => showStallsByMerchantModal = false}>
                        {stall.name}
                    </a> - {stall.description}
                </li>
            {/each}
        </ul>
    </div>
</div>
