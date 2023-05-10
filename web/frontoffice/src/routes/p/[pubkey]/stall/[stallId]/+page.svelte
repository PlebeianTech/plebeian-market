<script lang="ts">
    import ProductList from "$lib/components/stores/ProductList.svelte";
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import Expand from "$sharedLib/components/icons/Expand.svelte";
    import Contract from "$sharedLib/components/icons/Contract.svelte";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import {onMount} from "svelte";
    import {NostrPool, stalls} from "$lib/stores";
    import {getStallsByMerchant, refreshStalls} from "$lib/shopping";
    import {getChannelIdForStall} from "$lib/nostr/utils";

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

<div class="lg:flex mx-auto my-4">
    <div class="w-full px-4">
        <div class="grid justify-center items-center lg:mx-20 gap-6 place-content-center">
            <ProductList merchantPubkey={data.pubkey} stallId={data.stallId}></ProductList>
        </div>
    </div>

    {#if nostrRoomId !== null}
        <div class="grid top-20 px-4 lg:px-0 my-2 px-2 w-fit lg:w-3/6 max-h-screen overflow-y-auto lg:overflow-y-hidden place-items-top text-center">
            <h3 class="text-2xl lg:text-3xl ">Stall Chat</h3>

            <div class="btn-group float-right hidden md:visible">
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
