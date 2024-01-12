<script lang="ts">
    import {formatTimestamp} from "$sharedLib/nostr/utils";
    import Countdown, { CountdownStyle } from "$sharedLib/components/Countdown.svelte";
    import {goto} from "$app/navigation";

    export let product;

    export let reducedCard: boolean = false;

    let now: number = 0;
    let endsAt: number = 0;
    let ended: boolean = false;
    let started: boolean = false;

    $: if (product) {
        now = Math.floor(Date.now() / 1000);
        endsAt = product.start_date + product.duration;
        ended = now > endsAt;
        started = now > product.start_date;
    }
</script>

{#if product && product.start_date}
    <div>
        {#if ended}
            <h3 class="text-xl text-center my-2">
                Auction ended at {formatTimestamp(endsAt, true)}
            </h3>

        {:else} <!-- not ended -->
            {#if started}
                <div>
                    <p class="text-sm lg:text-base mt-1 lg:my-2">Ends in</p>
                    <div class="hidden lg:block">
                        <Countdown totalSeconds={endsAt - now} bind:ended={ended} />
                    </div>
                    <div class="block lg:hidden">
                        <Countdown totalSeconds={endsAt - now} style={CountdownStyle.Compact} bind:ended={ended} />
                    </div>
                </div>

            {:else}
                Auction starts at {formatTimestamp(product.start_date, true)} and will run for {product.duration / 60} hours until {formatTimestamp(product.start_date + product.duration, true)}.
                <div class="divider"></div>
            {/if}

            {#if !reducedCard}
                <div class="mt-1 justify-end">
                    <button class="btn btn-primary mt-4" on:click|preventDefault={() => goto('/product/' + product.id)}>
                        {#if started && !ended}
                            Bid
                        {:else}
                            View
                        {/if}
                    </button>
                </div>
            {/if}
        {/if}
    </div>
{/if}
