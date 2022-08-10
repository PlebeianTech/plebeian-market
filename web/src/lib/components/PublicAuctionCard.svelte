<script lang="ts">
    import type { Auction } from "../types/auction";
    import Countdown from "./Countdown.svelte";
    import { ErrorHandler, unfeatureAuction } from "../services/api";
    import { Error, Info, token, user } from "../stores";
    import SvelteMarkdown from 'svelte-markdown';

    function unfeature() {
        unfeatureAuction($token, entity.key,
            () => {
                Info.set("This auction will be prevented from being featured.");
            },
            new ErrorHandler(false, () => Error.set("Failed to unfeature the entity.")));
    }

    export let entity: Auction;
</script>

<div class="my-3 self-center glowbox">
    <div class="card bg-base-300 overflow-hidden shadow-xl my-3">
        <figure class="md:h-max flex justify-center">
            {#each entity.media as photo, i}
                {#if i === 0}
                    <img class="h-full md:max-h-80 object-fill" src={photo.url} alt="Auctioned object" />
                {/if}
            {/each}
        </figure>
        <div class="card-body">
            <h2 class="justify-center underline card-title mb-2">
                <a href="/auctions/{entity.key}">{entity.title}</a>
            </h2>
            <div class="badge badge-primary self-center md:float-right">{entity.bids.length} bids</div>
            <div class="markdown-container max-h-52 overflow-hidden">
                <SvelteMarkdown source={entity.description} />
            </div>
            <hr class="border-solid divide-y-0 border-accent opacity-100 mb-2 mt-2">
            {#if !entity.ended}
                <Countdown untilDate={entity.end_date} />
            {/if}
            {#if $user && $user.isModerator && !entity.ended}
                <div class="btn btn-xs self-center md:float-right" on:click|preventDefault={unfeature}>Unfeature</div>
            {/if}
        </div>
    </div>
</div>