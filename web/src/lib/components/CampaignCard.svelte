<script lang="ts">
    import { onMount } from "svelte";
    import { deleteEntity } from "../services/api";
    import type { IEntity } from "$lib/types/base";
    import type { Campaign } from "$lib/types/campaign";
    import { token } from "$lib/stores";
    import Confirmation from "./Confirmation.svelte";

    export let entity: IEntity;
    $: campaign = <Campaign>entity;

    let confirmation: any = null;

    export let onEdit = (_: Campaign) => {};
    export let onView = (_: Campaign) => {};
    export let onDelete = () => {};

    function view() {
        onView(campaign);
        window.open(getUrl(), "_blank");
    }

    function getUrl() {
        return `${window.location.protocol}//${window.location.host}/campaigns/${campaign.key}`;
    }

    function del() {
        confirmation = {
            onContinue: () => {
                deleteEntity($token, campaign, onDelete);
            }
        };
    }

    onMount(async () => { confirmation = null; });
</script>

<div class="glowbox">
<div class="card md:card-side bg-base-300 max-w-full overflow-hidden shadow-xl my-3">
    <div class="card-body">
        <h2 class="card-title mb-2">
            {campaign.title}
            {#if campaign.started && !campaign.ended}
                <div class="badge badge-primary">running</div>
            {:else if campaign.ended}
                <div class="badge badge-secondary">ended</div>
            {/if}
        </h2>
        <div class="mt-2 card-actions justify-end">
            {#if confirmation}
                <Confirmation onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
            {:else}
                {#if !campaign.started}
                    <button class="btn mx-1" on:click={() => onEdit(campaign)}>Edit</button>
                    <button class="btn mx-1" on:click={del}>Delete</button>
                    <button class="btn mx-1" on:click={view}>View</button>
                {/if}
            {/if}
        </div>
    </div>
</div>
</div>