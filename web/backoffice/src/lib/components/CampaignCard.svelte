<script lang="ts">
    import { onMount } from "svelte";
    import SvelteMarkdown from 'svelte-markdown';
    import { deleteEntity } from "$lib/services/api";
    import { token } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import type { Campaign } from "$lib/types/campaign";
    import Confirmation from "$lib/components/Confirmation.svelte";

    export let isEditable = false;

    // svelte-ignore unused-export-let
    export let showCampaign = false;
    // svelte-ignore unused-export-let
    export let showOwner = false;

    export let entity: IEntity;
    $: campaign = <Campaign>entity;

    let confirmation: any = null;

    export let onEdit = (_: Campaign) => {};
    export let onEntityChanged = () => {};

    function view() {
        window.open(getUrl());
    }

    function getUrl() {
        return `${window.location.protocol}//${window.location.host}/campaigns/${campaign.key}`;
    }

    function del() {
        confirmation = {
            onContinue: () => {
                deleteEntity($token, campaign, onEntityChanged);
            }
        };
    }

    onMount(async () => { confirmation = null; });
</script>

<div class="">
<div class="card md:card-side bg-base-300 max-w-full overflow-hidden shadow-xl my-3">
    <div class="card-body">
        <h2 class="card-title mb-2">
            {campaign.name}
        </h2>
        <div class="markdown-container">
            <SvelteMarkdown source={campaign.description} />
        </div>
        <div class="mt-2 card-actions justify-end">
            {#if confirmation}
                <Confirmation onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
            {:else}
                {#if isEditable}
                    <button class="btn mx-1" on:click={() => onEdit(campaign)}>Edit</button>
                    <button class="btn mx-1" on:click={del}>Delete</button>
                {/if}
                <button class="btn mx-1" on:click={view}>View</button>
            {/if}
        </div>
    </div>
</div>
</div>