<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { UserAchievement } from "$lib/types/user";

    export let entity: IEntity;
    $: achievement = <UserAchievement>entity;
    export let onSave = () => {};
    export let onCancel = () => {};
</script>

<div class="w-full flex justify-center items-center">
    <div class="card bg-base-300 w-full lg:p-4 rounded shadow-2xl mt-3">
        <span class="btn btn-sm btn-circle absolute right-2 top-2" on:click={onCancel} on:keypress={onCancel}>✕</span>
        <div class="card-body items-center">
            <h2 class="card-title text-2xl text-center">{#if achievement.key}Edit achievement{:else}New achievement{/if}</h2>
            <form>
                <div class="form-control w-full max-w-full">
                    <label class="label" for="title">
                        <span class="label-text">Achievement</span>
                    </label>
                    <input bind:value={achievement.achievement} type="text" name="achievement" class="input input-bordered" />
                </div>
                <div class="flex mt-3">
                    <div class="form-control w-1/2 max-w-xs mr-1">
                        <label class="label" for="from_year">
                            <span class="label-text">From year</span>
                        </label>
                        <input bind:value={achievement.from_year} type="number" name="from_year" class="input input-bordered w-full max-w-xs" />
                    </div>
                    <div class="form-control w-1/2 max-w-xs ml-1">
                        <label class="label" for="from_month">
                            <span class="label-text">From month (number)</span>
                        </label>
                        <input bind:value={achievement.from_month} type="number" name="from_month" class="input input-bordered w-full max-w-xs" />
                    </div>
                </div>
                <div class="flex mt-3">
                    <div class="form-control w-1/2 max-w-xs mr-1">
                        <label class="label" for="to_year">
                            <span class="label-text">To year</span>
                        </label>
                        <input bind:value={achievement.to_year} type="number" name="to_year" class="input input-bordered w-full max-w-xs" />
                    </div>
                    <div class="form-control w-1/2 max-w-xs ml-1">
                        <label class="label" for="to_month">
                            <span class="label-text">To month (number)</span>
                        </label>
                        <input bind:value={achievement.to_month} type="number" name="to_month" class="input input-bordered w-full max-w-xs" />
                    </div>
                </div>
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    {#if !achievement.validate()}
                        <button class="btn mt-1" disabled>Save</button>
                    {:else}
                        <button class="btn btn-secondary" on:click|preventDefault={onSave} on:keypress={onSave}>Save</button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>
