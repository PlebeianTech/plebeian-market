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
            <form class="w-full">
                {#if campaign.key === null || campaign.key === ""}
                    <div class="alert alert-info shadow-lg">
                        <div>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            <span>
                                We use your XPUB to generate addresses for your payments.
                                We strongly suggest you use a separate wallet for this campaign only!
                            </span>
                        </div>
                    </div>
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
                <MarkdownDescriptionEditor bind:value={campaign.description} />
            </form>
            <div class="w-full flex justify-center items-center mt-2">
                <div class="w-1/2 flex justify-center items-center">
                    <button class="btn mt-1" on:click|preventDefault={onCancel}>Cancel</button>
                </div>
                <div class="w-1/2 flex justify-center items-center">
                    {#if campaign.xpub === null || campaign.xpub.length === 0 || campaign.name.length === 0 || campaign.description.length === 0}
                        <button class="btn mt-1" disabled>Save</button>
                    {:else}
                        <div class="glowbutton glowbutton-save" on:click|preventDefault={onSave}></div>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div>