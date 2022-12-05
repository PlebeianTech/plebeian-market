<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import type { IEntity } from "$lib/types/base";
    import type { Auction } from "$lib/types/auction";
    import { Category } from "$lib/types/item";
    import { user } from "$lib/stores";
    import { isProduction } from "$lib/utils";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import MarkdownDescriptionEditor from "$lib/components/MarkdownDescriptionEditor.svelte";
    import ShippingEditor from "$lib/components/ShippingEditor.svelte";

    export let entity: IEntity;
    $: auction = <Auction>entity;
    export let onSave = () => {};
    export let onCancel = () => {};

    $: isTimeAuction = auction.category === Category.Time;

    function setTitle(user) {
        if (user && user.nym && auction && isTimeAuction) {
            auction.title = `1 hour one-to-one call with ${user.nym} AMA`;
        }
    }

    onDestroy(user.subscribe(setTitle));

    let duration = "";
    let durationMultiplier = "1";
    $: durationOptions = isProduction()
        ? [1, 24, 2 * 24]
        : [0.1, 1, 24];
    $: durationLabels = isProduction()
        ? ["1 hour", "1 day", "2 days"]
        : ["6 minutes", "1 hour", "1 day"];

    function twelveHours() {
        auction.duration_hours = 12;
        customDuration();
    }

    function customDuration() {
        if (auction.duration_hours % 24 === 0) {
            durationMultiplier = "24";
            duration = (auction.duration_hours / 24).toString();
        } else {
            durationMultiplier = "1";
            duration = auction.duration_hours.toString();
        }
    }

    function customChanged() {
        auction.duration_hours = parseInt(duration) * parseInt(durationMultiplier);
    }

    onMount(async () => {
        setTitle($user);
        if (isTimeAuction) {
            auction.duration_hours = isProduction() ? 48 : 0.1;
        }
        customDuration();
    });
</script>

<div class="w-full flex justify-center items-center">    
    <div class="card bg-base-300 w-full lg:p-4 rounded shadow-2xl mt-3">
        <span class="btn btn-sm btn-circle absolute right-2 top-2" on:click={onCancel}>✕</span>
        <div class="card-body items-center">
            <h2 class="card-title text-2xl text-center">{#if auction.key}Edit auction{:else}New auction{/if}</h2>
            <form class="w-full">
                <div class="form-control w-full max-w-full">
                    <label class="label" for="title">
                        <span class="label-text">Title</span>
                    </label>
                    <input bind:value={auction.title} type="text" name="title" class="input input-bordered" />
                </div>
                <MarkdownDescriptionEditor bind:value={auction.description} placeholder={auction.descriptionPlaceholder} />
                {#if !isTimeAuction}
                    <div class="flex mt-3">
                        <div class="form-control w-1/2 max-w-xs mr-1">
                            <label class="label" for="starting-bid">
                                <span class="label-text">Starting bid (optional)</span>
                            </label>
                            <input bind:value={auction.starting_bid} type="number" name="starting-bid" class="input input-bordered w-full max-w-xs" />
                            <label class="label" for="starting-bid">
                                <span class="label-text-alt"><AmountFormatter satsAmount={auction.starting_bid} format={AmountFormat.Usd} /></span>
                                <span class="label-text-alt">sats</span>
                            </label>
                        </div>
                        <div class="form-control w-1/2 max-w-xs ml-1">
                            <label class="label" for="reserve-bid">
                                <span class="label-text">Reserve bid (optional)</span>
                            </label>
                            <input bind:value={auction.reserve_bid} type="number" name="reserve-bid" class="input input-bordered w-full max-w-xs" />
                            <label class="label" for="reserve-bid">
                                <span class="label-text-alt"><AmountFormatter satsAmount={auction.reserve_bid} format={AmountFormat.Usd} /></span>
                                <span class="label-text-alt">sats</span>
                            </label>
                        </div>
                    </div>
                    {/if}
                {#if !isTimeAuction} <!-- shipping -->
                    <ShippingEditor
                        bind:shipping_from={auction.shipping_from}
                        bind:shipping_domestic_usd={auction.shipping_domestic_usd}
                        bind:shipping_worldwide_usd={auction.shipping_worldwide_usd} />
                {/if} <!-- /shipping -->
                {#if !isTimeAuction} <!-- duration -->
                    <div class="form-control mr-2 w-full">
                        <label class="label" for="duration">
                            <span class="label-text text-lg">Auction Duration</span>
                        </label>
                        <div class="flex flex-wrap">
                            {#each durationOptions as duration, i}
                                <button class:btn-outline={auction.duration_hours !== duration} class:btn-active={auction.duration_hours === duration} class="mx-2 mt-2 btn btn-accent btn-outline flex-auto" on:click|preventDefault={() => auction.duration_hours = duration}>{durationLabels[i]}</button>
                            {/each}
                            <button class:btn-outline={durationOptions.indexOf(auction.duration_hours) !== -1} class:btn-active={durationOptions.indexOf(auction.duration_hours) == -1} class="mx-2 mt-2 btn btn-accent btn-outline flex-auto" on:click|preventDefault={twelveHours}>Custom</button>
                            <input type="hidden" name="duration-hours" bind:value={auction.duration_hours} />
                            <div class:invisible={durationOptions.indexOf(auction.duration_hours) !== -1} class="flex mx-2 mt-2 w-2/4 flex-auto">
                                <div class="form-control max-w-xs mr-1 w-1/4 flex-auto">
                                    <input bind:value={duration} on:change={customChanged} type="number" name="duration" class="input input-bordered w-full max-w-xs" />
                                </div>
                                <select bind:value={durationMultiplier} on:change={customChanged} class="select select-bordered w-2/4 max-w-xs ml-1 flex-auto" name="duration-multiplier" id="duration-multiplier">
                                    <option value="1">Hours</option>
                                    <option value="24">Days</option>
                                </select>
                            </div>
                        </div>
                    </div>
                {/if} <!-- /duration -->
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    {#if !auction.validate()}
                        <button class="btn mt-1" disabled>Save</button>
                    {:else}
                        <div class="glowbutton" class:glowbutton-save={!isTimeAuction} class:glowbutton-publish={isTimeAuction} on:click|preventDefault={onSave}></div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>
