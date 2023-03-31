<script lang="ts">
    import { onMount } from 'svelte';
    import { NostrPool } from "$lib/stores";
    import {subscribeProducts} from "../../services/nostr";
    import {NostrStall} from "../../types/nip45";
    import ProductCard from "$lib/components/stores/ProductCard.svelte";
    import ProductRow from "$lib/components/stores/ProductRow.svelte";
    import {getFirstTagValue} from "../../nostr/utils";

    export let merchant_pubkey: string;
    export let stall_id: string;

    let products: {[product_id: string]: {}} = {};

    let listView = false    ;

    onMount(
        async () => {
            subscribeProducts($NostrPool, merchant_pubkey,
                (productEvent) => {
                    let content = JSON.parse(productEvent.content);
                    content.created_at = productEvent.created_at;
                    content.merchantPubkey = productEvent.pubkey;

                    if (!content.id) {
                        let product_id = getFirstTagValue(productEvent.tags, 'd');
                        if (product_id !== null) {
                            content.id = product_id;
                        } else {
                            return;
                        }
                    }

//console.log('productEvent content', content);

                    let product_id = content.id;

                    if (content.stall_id === stall_id) {
//console.log('       ** Viewing content:', content);
                        if (product_id in products) {
                            if (products[product_id].createdAt < productEvent.created_at) {
                                products[product_id] = content;
                            }
                        } else {
                            products[product_id] = content;
                        }
                    }
            });
        }
    );
</script>

<div class="btn-group btn-group-vertical lg:btn-group-horizontal justify-end">
    <button class="btn" class:btn-active={listView} on:click={() => listView=true}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 1.5v-1.5m0 0c0-.621.504-1.125 1.125-1.125m0 0h7.5" />
        </svg>
    </button>
    <button class="btn" class:btn-active={!listView} on:click={() => listView=false}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
        </svg>
    </button>
</div>

{#if listView}
    <table class="table table-auto table-zebra w-full place-content-center">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Image</th>
                <th></th>
            </tr>
        </thead>

        <tbody>
            {#each Object.entries(products) as [product_id, product]}
                <ProductRow {product}></ProductRow>
            {/each}
        </tbody>
    </table>
{:else}
    <div class="p-2 py-2 pt-1 h-auto container grid lg:grid-cols-3 gap-6 place-content-center">
        {#each Object.entries(products) as [product_id, product]}
            <ProductCard {product}></ProductCard>
        {/each}
    </div>
{/if}
