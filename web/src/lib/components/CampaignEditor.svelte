<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Campaign } from "$lib/types/campaign";
    import MarkdownEditor from "$lib/components/MarkdownEditor.svelte";
    import XpubInfo from "$lib/components/XpubInfo.svelte";

    export let entity: IEntity;
    $: campaign = <Campaign>entity;
    export let onSave = () => {};
    export let onCancel = () => {};
</script>

<div class="w-full flex justify-center items-center">
    <div class="card bg-base-300 w-full lg:p-4 rounded shadow-2xl mt-3">
        <div class="card-body items-center">
            <h2 class="card-title mb-4 text-2xl text-center">{#if campaign.key}Edit campaign{:else}New campaign{/if}</h2>
            <form class="w-full">
                {#if campaign.key === null || campaign.key === ""}
                    <XpubInfo></XpubInfo>
                    <div class="form-control w-full max-w-full">
                        <label class="label" for="xpub">
                            <span class="label-text">XPUB</span>
                        </label>
                        <input bind:value={campaign.xpub} type="text" name="xpub" class="input input-bordered" />
                    </div>
                {/if}
                <div class="form-control w-full max-w-full">
                    <label class="label" for="name">
                        <span class="label-text">Name</span>
                    </label>
                    <input bind:value={campaign.name} type="text" name="name" class="input input-bordered w-full" />
                </div>
                <MarkdownEditor bind:value={campaign.description} />
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    {#if campaign.xpub === null || campaign.xpub.length === 0 || campaign.name.length === 0 || campaign.description.length === 0}
                        <button class="btn mt-1" disabled>Save</button>
                    {:else}
                        <button class="btn btn-primary" on:click|preventDefault={onSave}>Save</button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>
