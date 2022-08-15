<script lang="ts">
    import SvelteMarkdown from 'svelte-markdown';
    import { Auction } from "$lib/types/auction";
    import type { IEntity } from "$lib/types/base";
    import type { Item } from "$lib/types/item";
    import { Listing } from "$lib/types/listing";
    import { ErrorHandler, hideAuction } from "$lib/services/api";
    import { Error, Info, token, user } from "$lib/stores";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import Countdown from "$lib/components/Countdown.svelte";

    function hide() {
        hideAuction($token, item.key,
            () => {
                Info.set("This auction will be prevented from being featured.");
            },
            new ErrorHandler(false, () => Error.set("Failed to hide the item.")));
    }

    export let entity: IEntity;
    $: item = <Item>(<unknown>entity);
</script>

<div class="my-3 self-center glowbox">
    <div class="card bg-base-300 overflow-hidden shadow-xl my-3">
        <figure class="md:h-max flex justify-center">
            {#each item.media as photo, i}
                {#if i === 0}
                    <img class="h-full object-fill" src={photo.url} alt="Auctioned object" />
                {/if}
            {/each}
        </figure>
        <div class="card-body">
            <h2 class="justify-center underline card-title mb-2">
                <a href="/{item.endpoint}/{item.key}">{item.title}</a>
            </h2>
            {#if item instanceof Auction}
                <div class="badge badge-secondary">auction</div>
                <div class="badge badge-primary">{item.bids.length} bids</div>
            {:else if item instanceof Listing}
                <div class="badge badge-secondary">fixed price</div>
                <div class="badge badge-primary"><AmountFormatter usdAmount={item.price_usd} format={AmountFormat.Usd} /></div>
                <div class="badge badge-primary">~<AmountFormatter usdAmount={item.price_usd} format={AmountFormat.Sats} /></div>
            {/if}
            <div class="markdown-container max-h-52 overflow-hidden">
                <SvelteMarkdown source={item.description} />
            </div>
            <hr class="border-solid divide-y-0 border-accent opacity-100 mb-2 mt-2">
            {#if item instanceof Auction && !item.ended}
                <Countdown untilDate={item.end_date} />
            {/if}
            {#if $user && $user.isModerator}
                <div class="btn btn-xs self-center md:float-right" on:click|preventDefault={hide}>Hide</div>
            {/if}
        </div>
    </div>
</div>