<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Campaign } from "$lib/types/campaign";
    import MarkdownDescriptionEditor from "$lib/components/MarkdownDescriptionEditor.svelte";

    export let entity: IEntity;
    $: campaign = <Campaign>entity;
    export let onSave = () => {};
    export let onCancel = () => {};
</script>

<div class="w-full flex justify-center items-center">
    <div class="card bg-base-300 w-full lg:p-4 rounded shadow-2xl mt-3">
        <div class="card-body items-center">
            <h2 class="card-title mb-4 text-2xl text-center">{#if campaign.key}Edit campaign{:else}New campaign{/if}</h2>
            <form>
                <div class="form-control w-full max-w-xs">
                    <label class="label" for="title">
                        <span class="label-text">Title</span>
                    </label>
                    <input bind:value={campaign.title} type="text" name="title" class="input input-bordered w-full max-w-xs" />
                </div>
                <MarkdownDescriptionEditor bind:value={campaign.description} />
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    {#if campaign.title.length === 0 || campaign.description.length === 0}
                        <button class="btn mt-1" disabled>Save</button>
                    {:else}
                        <div class="glowbutton glowbutton-save" on:click|preventDefault={onSave}></div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>
