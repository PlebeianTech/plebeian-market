<script lang="ts">
    import { onMount } from 'svelte';
    import { NostrPool, Error } from "$lib/stores";
    import {subscribeProducts} from "../../services/nostr";
    import ProductCard from "$lib/components/stores/ProductCard.svelte";
    import ProductRow from "$lib/components/stores/ProductRow.svelte";
    import {getFirstTagValue} from "../../nostr/utils";
    import {onImgError} from "$lib/shopping";
    import ViewList from "$lib/components/icons/ViewList.svelte";
    import ViewCards from "$lib/components/icons/ViewCards.svelte";

    export let merchantPubkey: string;
    export let stallId: string;

    let products: {[productId: string]: {}} = {};

    let listView = false;

    onMount(async () => {
        subscribeProducts($NostrPool, merchantPubkey,
            (productEvent) => {
                let content = JSON.parse(productEvent.content);
                content.createdAt = productEvent.created_at;
                content.merchantPubkey = productEvent.pubkey;

                if (!content.id) {
                    let productId = getFirstTagValue(productEvent.tags, 'd');
                    if (productId !== null) {
                        content.id = productId;
                    } else {
                        return;
                    }
                }

                let productId = content.id;

                if (content.stallId === stallId) {
                    if (productId in products) {
                        if (products[productId].createdAt < productEvent.created_at) {
                            products[productId] = content;
                        }
                    } else {
                        products[productId] = content;
                    }
                }
            });
    });
</script>

<div class="btn-group btn-group-vertical lg:btn-group-horizontal justify-end">
    <button class="btn" class:btn-active={listView} on:click={() => listView=true}>
        <ViewList />
    </button>
    <button class="btn" class:btn-active={!listView} on:click={() => listView=false}>
        <ViewCards />
    </button>
</div>

{#if listView}
    <table class="table table-auto table-zebra w-full place-content-center">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Stock</th>
                <th>Price</th>
                <th>Image</th>
                <th></th>
            </tr>
        </thead>

        <tbody>
            {#each Object.entries(products) as [productId, product]}
                <ProductRow {product} {onImgError}></ProductRow>
            {/each}
        </tbody>
    </table>
{:else}
    <div class="p-2 py-2 pt-1 h-auto container grid lg:grid-cols-3 gap-6 place-content-center">
        {#each Object.entries(products) as [productId, product]}
            <ProductCard {product} {onImgError}></ProductCard>
        {/each}
    </div>
{/if}
