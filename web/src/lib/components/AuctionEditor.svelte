<script lang="ts">
    import { onMount } from 'svelte';
    import type { IEntity } from "$lib/types/base";
    import type { Auction } from "$lib/types/auction";
    import { isLocal, isStaging } from "$lib/utils";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import MarkdownDescriptionEditor from "$lib/components/MarkdownDescriptionEditor.svelte";

    export let entity: IEntity;
    $: auction = <Auction>entity;
    export let onSave = () => {};
    export let onCancel = () => {};

    let duration = "";
    let durationMultiplier = "1";
    $: durationOptions = isLocal() || isStaging()
        ? [0.1, 1, 24]
        : [1, 24, 2 * 24];
    $: durationLabels = isLocal() || isStaging()
        ? ["6 minutes", "1 hour", "1 day"]
        : ["1 hour", "1 day", "2 days"];

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
        customDuration();
    });
</script>

<div class="w-full flex justify-center items-center">
    <div class="card bg-base-300 w-full lg:w-4/6 lg:p-4 rounded shadow-2xl mt-3">
        <div class="card-body items-center">
            <h2 class="card-title text-2xl text-center">{#if auction.key}Edit auction{:else}New auction{/if}</h2>
            <form>
                <div class="form-control w-full max-w-full">
                    <label class="label" for="title">
                        <span class="label-text">Title</span>
                    </label>
                    <input bind:value={auction.title} type="text" name="title" class="input input-bordered" />
                </div>
                <MarkdownDescriptionEditor bind:value={auction.description} />
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
                <div class="form-control w-full max-w-xs mt-3">
                    <label class="label" for="shipping_from">
                        <span class="label-text">Shipping from (optional)</span>
                    </label>
                    <input bind:value={auction.shipping_from} type="text" name="shipping_from" class="input input-bordered w-full max-w-xs" />
                </div>
                <div class="form-control mr-2 w-full">
                    <label class="label" for="duration">
                        <span class="label-text">Duration</span>
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
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    {#if auction.title.length === 0 || auction.description.length === 0}
                        <button class="btn mt-1" disabled>Save</button>
                    {:else}
                        <div class="glowbutton glowbutton-save" on:click|preventDefault={onSave}></div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>
