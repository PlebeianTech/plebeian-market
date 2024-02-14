<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import { ErrorHandler, getStatus, putUpdate } from "$lib/services/api";
    import { Info, token } from "$sharedLib/stores";

    export let onSave: () => void = () => {};

    let version: string | null = null;
    let lastVersion: string | null = null;
    let githubRepoUrl: string | null = null;

    let inRequest = false;
    function update() {
        inRequest = true;
        putUpdate($token,
            () => {
                Info.set("Update requested!");
                inRequest = false;
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    let updateButtonActive = version !== lastVersion && !inRequest;

    onMount(async () => {
        getStatus((v, lv, g) => { version = v; lastVersion = lv; githubRepoUrl = g; });
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>App</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">App</h2>
{/if}

{#if version !== null && lastVersion !== null}
    <div class="items-center justify-center mt-8">
        <p class="text-2xl">You are currently running<br /><strong>Plebeian Market {version}</strong>.</p>
        {#if version === lastVersion}
            <p class="text-xl mt-4">This is the most recent version. All is well!</p>
        {:else}
            <p class="text-2xl mt-4">The last available version is <strong>{lastVersion}</strong>.</p>
            {#if githubRepoUrl !== null}
                <p class="text-xl mt-4">See what is new <a class="link" target="_blank" href="{githubRepoUrl}/releases/">here</a>!</p>
            {/if}
        {/if}
    </div>
    <div class="flex justify-center items-center mt-8 h-15">
        <button id="update-pm" class="btn btn-primary" class:btn-disabled={!updateButtonActive} on:click|preventDefault={update}>Update</button>
    </div>
{:else}
    <div class="items-center justify-center mt-8">
        <p class="text-2xl">Running <strong>Plebeian Market</strong>.</p>
    </div>
{/if}