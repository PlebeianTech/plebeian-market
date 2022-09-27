<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import MarkdownDescriptionEditor from "$lib/components/MarkdownDescriptionEditor.svelte";

    export let onSave: () => void = () => {};

    let stallName: string | null = null;
    let stallDescription: string = "";

    $: saveButtonActive = $user && !saving && (stallName !== $user.stallName || stallDescription !== $user.stallDescription);

    let saving = false;
    function save() {
        saving = true;
        putProfile($token, {stallName, stallDescription},
            u => {
                user.set(u);
                Info.set("Your stall details have been saved!");
                stallName = u.stallName;
                stallDescription = u.stallDescription;
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            stallName = $user.stallName ? `${$user.stallName}` : "";
            stallDescription = $user.stallDescription ? `${$user.stallDescription}` : "";
        }
    });
</script>

{#if $page.url.pathname === "/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>My Stall</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">My Stall</h2>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <label class="label" for="stallName">
            <span class="label-text">Title</span>
        </label>
        <input bind:value={stallName} id="stallName" name="stallName" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>
<MarkdownDescriptionEditor bind:value={stallDescription} />

<div class="flex justify-center items-center mt-4 h-15">
    {#if saveButtonActive}
        <div id="save-profile" class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>
