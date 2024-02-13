<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import { getStatus } from "$lib/services/api";

    export let onSave: () => void = () => {};

    let updateButtonActive = false;

    let version;

    let saving = false;
    function update() {
    }

    onMount(async () => {
        getStatus((v) => { version = v; });
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>Version</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">Version</h2>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <p class="text-2xl">You are currently running Plebeian Market {version}.</p>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="update-pm" class="btn btn-primary" class:btn-disabled={!updateButtonActive} on:click|preventDefault={update}>Update</button>
</div>
