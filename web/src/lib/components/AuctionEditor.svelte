<script lang="ts">
    import { onMount } from 'svelte';
    import type { Auction } from "../types/auction";

    export let auction: Auction;
    export let onSave = () => {};
    export let onCancel = () => {};

    let duration = "";
    let durationMultiplier = "1";

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

    onMount(async () => { customDuration() });
</script>

<div class="w-full flex justify-center items-center">
    <div class="card bg-base-100 w-4/6 p-4 rounded shadow-xl my-3 glowbox">
        <h2 class="card-title mb-4 text-2xl text-center">{#if auction.key}Edit auction{:else}New auction{/if}</h2>
        <form>
            <div class="form-control w-full max-w-xs">
                <label class="label" for="title">
                    <span class="label-text">Title</span>
                </label>
                <input bind:value={auction.title} type="text" name="title" class="input input-bordered w-full max-w-xs" />
            </div>
            <div class="form-control">
                <label class="label" for="description">
                    <span class="label-text">Description</span>
                </label>
                <textarea bind:value={auction.description} rows="4" class="textarea textarea-bordered h-24" placeholder=""></textarea>
            </div>
            <div class="flex">
                <div class="form-control w-1/2 max-w-xs mr-1">
                    <label class="label" for="starting-bid">
                        <span class="label-text">Starting bid (optional)</span>
                    </label>
                    <input bind:value={auction.starting_bid} type="number" name="starting-bid" class="input input-bordered w-full max-w-xs" />
                    <label class="label" for="starting-bid">
                        <span class="label-text-alt"></span>
                        <span class="label-text-alt">sats</span>
                    </label>
                </div>
                <div class="form-control w-1/2 max-w-xs ml-1">
                    <label class="label" for="reserve-bid">
                        <span class="label-text">Reserve bid (optional)</span>
                    </label>
                    <input bind:value={auction.reserve_bid} type="number" name="reserve-bid" class="input input-bordered w-full max-w-xs" />
                    <label class="label" for="reserve-bid">
                        <span class="label-text-alt"></span>
                        <span class="label-text-alt">sats</span>
                    </label>
                </div>
            </div>
            <div class="form-control mr-2 w-full">
                <label class="label" for="duration">
                    <span class="label-text">Duration</span>
                </label>
                <div class="flex">
                    <button class:btn-outline={auction.duration_hours !== 0.1} class:btn-active={auction.duration_hours === 0.1} class="mx-2 btn btn-accent btn-outline" on:click|preventDefault={() => auction.duration_hours = 0.1}>Six minutes</button>
                    <button class:btn-outline={auction.duration_hours !== 1} class:btn-active={auction.duration_hours === 1} class="mx-2 btn btn-accent btn-outline" on:click|preventDefault={() => auction.duration_hours = 1}>An hour</button>
                    <button class:btn-outline={auction.duration_hours !== 24} class:btn-active={auction.duration_hours === 24} class="mx-2 btn btn-accent btn-outline" on:click|preventDefault={() => auction.duration_hours = 24}>A day</button>
                    <button class:btn-outline={auction.duration_hours === 0.1 || auction.duration_hours === 1 || auction.duration_hours === 24} class:btn-active={auction.duration_hours !== 0.1 && auction.duration_hours !== 1 && auction.duration_hours !== 24} class="mx-2 btn btn-accent btn-outline" on:click|preventDefault={twelveHours}>Custom</button>
                    <input type="hidden" name="duration-hours" bind:value={auction.duration_hours} />
                </div>
                <div class:invisible={auction.duration_hours === 0.1 || auction.duration_hours === 1 || auction.duration_hours === 24} class="flex ml-4 mt-2 w-full">
                    <div class="form-control max-w-xs mr-1 w-1/4">
                        <input bind:value={duration} on:change={customChanged} type="number" name="duration" class="input input-bordered w-full max-w-xs" />
                    </div>
                    <select bind:value={durationMultiplier} on:change={customChanged} class="select select-bordered w-1/4 max-w-xs ml-1" name="duration-multiplier" id="duration-multiplier">
                        <option value="1">Hours</option>
                        <option value="24">Days</option>
                    </select>
                </div>
            </div>
        </form>
    </div>
</div>
<div class="w-full flex justify-center items-center">
    <div class="w-4/6">
        <div class="float-left pt-5">
            <button class="btn" on:click|preventDefault={onCancel}>Cancel</button>
        </div>
        <div class="float-right pt-5">
            {#if auction.title.length === 0 || auction.description.length === 0}
                <button class="btn" disabled>Save</button>
            {:else}
                <div class="glowbutton glowbutton-save" on:click|preventDefault={onSave}></div>
            {/if}
        </div>
    </div>
</div>