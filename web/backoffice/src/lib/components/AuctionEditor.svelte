<script lang="ts">
    import { onMount } from 'svelte';
    import type { IEntity } from "$lib/types/base";
    import type { Auction } from "$lib/types/auction";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import MarkdownEditor from "$lib/components/MarkdownEditor.svelte";
    import MediaEditor from "$lib/components/MediaEditor.svelte";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";

    export let entity: IEntity;
    $: auction = <Auction>entity;
    export let onSave = () => {};
    export let onCancel = () => {};

    let duration = "";
    let durationMultiplier = "1";
    $: durationOptions = [2 * 24];
    $: durationLabels = ["48 hours"];

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
    <div class="card bg-base-300 w-full lg:p-4 rounded shadow-2xl mt-3">
        <span class="btn btn-sm btn-circle absolute right-2 top-2" on:click={onCancel} on:keypress={onCancel}>✕</span>
        <div class="card-body items-center">
            <h2 class="card-title text-2xl text-center">{#if auction.key}Edit auction{:else}New auction{/if}</h2>
            <form class="w-full">
                <div class="form-control w-full max-w-full">
                    <label class="label" for="title">
                        <span class="label-text">Title</span>
                    </label>
                    <input bind:value={auction.title} type="text" name="title" class="input input-bordered" />
                </div>
                <MarkdownEditor bind:value={auction.description} placeholder={auction.descriptionPlaceholder} />
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
                {#if (auction.key === null || auction.key === "")} <!-- duration -->
                    <div class="form-control mr-2 w-full">
                        <label class="label" for="duration">
                            <div class="label-text text-lg flex items-center justify-center gap-2">
                                Auction Duration
                                <div class="tooltip tooltip-top" data-tip="How long the auction will run for after it is published">
                                    <InfoIcon />
                                </div>
                            </div>
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
                <MediaEditor item={auction} />
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    <div class="tooltip tooltip-top" data-tip="Don't worry, this will not start the auction. You start it later by hitting Publish!">
                        {#if !auction.validate()}
                            <button class="btn mt-1" disabled>Save</button>
                        {:else}
                            <button class="btn btn-primary" on:click|preventDefault={onSave} on:keypress={onSave}>Save</button>                        
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
