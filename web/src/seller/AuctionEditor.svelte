<script>
    import { onMount } from 'svelte';

    export let auction = null;
    export let onSave = () => {};

    let duration = "";
    let durationMultiplier = "1";

    function twelveHours() {
        auction.duration_hours = 12;
        customDuration();
    }

    function customDuration() {
        if (auction.duration_hours % 24 === 0) {
            durationMultiplier = "24";
            duration = auction.duration_hours / 24;
        } else {
            durationMultiplier = "1";
            duration = auction.duration_hours;
        }
    }

    function customChanged() {
        auction.duration_hours = parseInt(duration) * parseInt(durationMultiplier);
    }

    onMount(async () => { customDuration() });
</script>

<style>
    .invalid {
        color: #991B1B;
    }
    .invalid-field {
        border-bottom: 2px solid #991B1B;
    }
</style>

<div class="w-full flex justify-center items-center">
    <div class="w-4/6 p-4 rounded shadow-lg bg-gray-900 my-3 glowbox">
        <h2 class="mb-4 text-2xl text-center text-white">{#if auction.key}Edit auction <code class="bg-cyan-600 p-1 rounded">{auction.key}</code>{:else}Create a new auction{/if}</h2>
        <form>
            <div class="flex">
            <div class="form-group mr-2 w-full">
                <input class="form-field" class:invalid-field={auction.invalidTitle && auction.title.length === 0} name="title" bind:value={auction.title} type="text" id="title" />
                <label class="form-label" class:invalid={auction.invalidTitle && auction.title.length === 0} for="title">Title</label>
            </div>
            </div>
            <div class="flex">
            <div class="form-group mr-2 w-full">
                <textarea class="form-field" rows="4" class:invalid-field={auction.invalidDescription && auction.description.length === 0} name="description" bind:value={auction.description} id="description"></textarea>
                <label class="form-label" class:invalid={auction.invalidDescription && auction.description.length === 0} for="reserve-bid">Description</label>
            </div>
            </div>
            <div class="flex">
                <div class="form-group mr-2 w-1/2">
                    <input class="form-field" name="starting-bid" bind:value={auction.starting_bid} type="number" id="starting-bid" />
                    <label class="form-label" for="starting-bid">Starting bid (optional)</label>
                </div>
                <div class="form-group ml-2 w-1/2">
                    <input class="form-field" name="reserve-bid" bind:value={auction.reserve_bid} type="number" id="reserve-bid" />
                    <label class="form-label" for="reserve-bid">Reserve bid (optional)</label>
                </div>
            </div>
            <div class="form-group mr-2 w-full">
                <div class="flex justify-center items-center">
                    <div class="w-1/3 mt-5 text-center">
                        <span class="text-indigo-200 mr-2 mt-5 p-2">Duration</span>
                    </div>
                    <div class="w-2/3 mt-5">
                        <div class="flex justify-center items-center">
                            <button class:btn-outline={auction.duration_hours !== 1} class:btn-active={auction.duration_hours === 1} class="mx-2 btn btn-accent btn-outline" on:click|preventDefault={() => auction.duration_hours = 1}>An hour</button>
                            <button class:btn-outline={auction.duration_hours !== 24} class:btn-active={auction.duration_hours === 24} class="mx-2 btn btn-accent btn-outline" on:click|preventDefault={() => auction.duration_hours = 24}>A day</button>
                            <button class:btn-outline={auction.duration_hours === 1 || auction.duration_hours === 24} class:btn-active={auction.duration_hours !== 1 && auction.duration_hours !== 24} class="mx-2 btn btn-accent btn-outline" on:click|preventDefault={twelveHours}>Custom</button>
                            <input type="hidden" name="duration-hours" bind:value={auction.duration_hours} />
                        </div>
                        <div class:invisible={auction.duration_hours === 1 || auction.duration_hours === 24} class="flex justify-center items-center">
                            <input bind:value={duration} class="form-field leading-none pr-2 mr-2" name="duration" type="number" id="duration" on:change={customChanged} />
                            <select bind:value={durationMultiplier} class="form-field leading-none" name="duration-multiplier" id="duration-multiplier" on:change={customChanged}>
                                <option value="1">Hours</option>
                                <option value="24">Days</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
</div>
<div class="w-full flex justify-center items-center">
    <div class="w-4/6">
        <div class="float-left pt-5">
            <div class:disabled={auction.title.length === 0 || auction.description.length === 0} class="glowbutton glowbutton-save" on:click|preventDefault={onSave}></div>
        </div>
        <div class="float-right pt-5">
            <button class="btn" on:click|preventDefault={() => auction = null}>Cancel</button>
        </div>
    </div>
</div>