<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import XpubInfo from "$lib/components/XpubInfo.svelte";

    export let onSave: () => void = () => {};

    let wallet: string | null = null;

    $: isValidInput = wallet !== null && wallet !== "";
    $: saveButtonActive = $user && isValidInput && !saving && wallet !== $user.wallet;

    let saving = false;
    function save() {
        if (!wallet) {
            // this would happen if somebody tries to call save when isValidInput is false
            return;
        }
        saving = true;
        putProfile($token, {wallet},
            u => {
                user.set(u);
                Info.set("Your wallet has been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            wallet = $user.wallet ? $user.wallet : "";
        }
    });
</script>

{#if $user}
    {#if $page.url.pathname === "/account/settings"}
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

<XpubInfo />

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <input bind:value={wallet} id="wallet" name="wallet" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    {#if saveButtonActive}
        <button id="save-profile" class="btn btn-primary" on:click|preventDefault={save}>Save</button>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>
