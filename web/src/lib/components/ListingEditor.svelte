<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { user } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Category } from "$lib/types/item";
    import type { Listing } from "$lib/types/listing";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import MarkdownDescriptionEditor from "$lib/components/MarkdownDescriptionEditor.svelte";
    import ShippingEditor from "$lib/components/ShippingEditor.svelte";

    export let entity: IEntity;
    $: listing = <Listing>entity;
    export let onSave = () => {};
    export let onCancel = () => {};

    function setTitle(user) {
        if (user && user.nym && listing && listing.category === Category.Time) {
            listing.title = `1 hour one-to-one video call with ${user.nym} AMA`;
        }
    }

    onDestroy(user.subscribe(setTitle));

    onMount(async () => {
        setTitle($user);
    });
</script>

<div class="w-full flex justify-center items-center">
    <div class="card bg-base-300 w-full lg:p-4 rounded shadow-2xl mt-3">
        <span class="btn btn-sm btn-circle absolute right-2 top-2" on:click={onCancel} on:keypress={onCancel}>✕</span>
        <div class="card-body items-center">
            <h2 class="card-title text-2xl text-center">{#if listing.key}Edit listing{:else}New listing{/if}</h2>
            <form>
                <div class="form-control w-full max-w-full">
                    <label class="label" for="title">
                        <span class="label-text">Title</span>
                    </label>
                    <input bind:value={listing.title} type="text" name="title" class="input input-bordered" />
                </div>
                <MarkdownDescriptionEditor bind:value={listing.description} placeholder={listing.descriptionPlaceholder} />
                <div class="flex mt-3">
                    <div class="form-control w-1/2 max-w-xs mr-1">
                        <label class="label" for="price_usd">
                            <span class="label-text">Price ($)</span>
                        </label>
                        <input bind:value={listing.price_usd} type="number" name="price_usd" class="input input-bordered w-full max-w-xs" />
                        <label class="label" for="price_usd">
                            <span class="label-text-alt"><AmountFormatter usdAmount={listing.price_usd} format={AmountFormat.Sats} /></span>
                            <span class="label-text-alt"></span>
                        </label>
                    </div>
                    <div class="form-control w-1/2 max-w-xs ml-1">
                        <label class="label" for="available-quantity">
                            <span class="label-text">Available quantity</span>
                        </label>
                        <input bind:value={listing.available_quantity} type="number" name="available-quantity" class="input input-bordered w-full max-w-xs" />
                    </div>
                </div>
                {#if listing.category !== Category.Time}
                    <ShippingEditor
                        bind:shipping_from={listing.shipping_from}
                        bind:shipping_domestic_usd={listing.shipping_domestic_usd}
                        bind:shipping_worldwide_usd={listing.shipping_worldwide_usd} />
                {/if}
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    {#if !listing.validate()}
                        <button class="btn mt-1" disabled>Save</button>
                    {:else}
                        <div class="glowbutton glowbutton-save" on:click|preventDefault={onSave} on:keypress={onSave}></div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>
