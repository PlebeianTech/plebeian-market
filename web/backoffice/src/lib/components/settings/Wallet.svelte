<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile, type UserProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import XpubInfo from "$lib/components/XpubInfo.svelte";

    export let onSave: () => void = () => {};

    let wallet: string | null = null;
    let lightningAddress: string | null = null;

    $: isValidWallet = wallet !== null && wallet !== "";
    $: saveWalletActive = $user && isValidWallet && !saving && wallet !== $user.wallet;

    $: isValidLightningAddress = lightningAddress !== null && lightningAddress !== "";
    $: saveLightningAddressActive = $user && isValidLightningAddress && !saving && lightningAddress !== $user.lightningAddress;

    let saving = false;
    function save(p: UserProfile) {
        saving = true;
        putProfile($token, p,
            (u, _) => {
                user.set(u);
                Info.set("Your profile has been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            wallet = $user.wallet ? $user.wallet : "";
            lightningAddress = $user.lightningAddress ? $user.lightningAddress : "";
        }
    });
</script>

{#if $user}
    {#if $page.url.pathname === "/admin/account/settings"}
        <div class="text-2xl breadcrumbs">
            <ul>
                <li>Settings</li>
                <li>Wallet</li>
            </ul>
        </div>
    {:else}
        <h2 class="text-2xl">Wallet</h2>
    {/if}
{/if}

<XpubInfo />

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <label class="label" for="stallName">
            <span class="label-text">XPUB / ZPUB</span>
        </label>
        <input bind:value={wallet} id="wallet" name="wallet" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save-wallet" class="btn btn-primary" class:btn-disabled={!saveWalletActive} on:click|preventDefault={() => { if (wallet) { save({wallet}) }}}>Save</button>
</div>

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <label class="label" for="stallName">
            <span class="label-text">Lightning address</span>
        </label>
        <input bind:value={lightningAddress} id="lightningAddress" name="lightningAddress" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save-lightning-address" class="btn btn-primary" class:btn-disabled={!saveLightningAddressActive} on:click|preventDefault={() => { if (lightningAddress) { save({lightningAddress}) }}}>Save</button>
</div>
