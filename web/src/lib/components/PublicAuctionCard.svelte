<script lang="ts">
    import { onMount } from "svelte";
    import type { Auction } from "../types/auction";
    import Countdown from "./Countdown.svelte";
    import DateFormatter from "./DateFormatter.svelte";
    export let auction : Auction;
</script>

<div class="w-2/3 my-3 self-center glowbox">
<div class="card md:card-side bg-base-300 max-w-full overflow-hidden shadow-xl my-3">
    <figure class="md:h-auto flex justify-center">
        {#each auction.media as photo, i}
            {#if i === 0}
                <img class="object-contain" src={photo.url} alt="Auctioned object" />
            {/if}
        {/each}
    </figure>
    <div class="card-body">
        <h2 class="justify-center card-title mb-2">
            {auction.title}
        </h2>
                                <Countdown untilDate={auction.end_date} />
                <span class="lg:float-right">{auction.bids.length} bids</span>
    </div>
</div>
</div>