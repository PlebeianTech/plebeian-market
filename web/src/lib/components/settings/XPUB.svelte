<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import XpubInfo from "$lib/components/XpubInfo.svelte";

    export let onSave: () => void = () => {};

    let xpub: string | null = null;

    $: isValidInput = xpub !== null && xpub !== "";
    $: saveButtonActive = $user && isValidInput && !saving && xpub !== $user.xpub;

    let saving = false;
    function save() {
        if (!xpub) {
            // this would happen if somebody tries to call save when isValidInput is false
            return;
        }
        saving = true;
        putProfile($token, {xpub},
            u => {
                user.set(u);
                Info.set("Your XPUB has been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            xpub = $user.xpub ? $user.xpub : "";
        }
    });
</script>

{#if $user}
    {#if $page.url.pathname === "/settings"}
        <div class="text-2xl breadcrumbs">
            <ul>
                <li>Settings</li>
                <li>My Wallet</li>
            </ul>
        </div>
    {:else}
        <h2 class="text-2xl">My wallet</h2>
    {/if}
{/if}

<XpubInfo></XpubInfo>

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <input bind:value={xpub} id="xpub" name="xpub" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    {#if saveButtonActive}
        <button id="save-profile" class="btn btn-primary" on:click|preventDefault={save}>Save</button>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>
