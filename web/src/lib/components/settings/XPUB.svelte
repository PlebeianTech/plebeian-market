<script lang="ts">
    import { onMount } from 'svelte';
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";

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

{#if !($user && $user.xpub)}
    <div class="alert alert-info shadow-lg">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>
                We use your XPUB to generate addresses for your payments.
                We strongly suggest you use a separate wallet for Plebeian Market only!
            </span>
        </div>
    </div>
{:else}
    <h2 class="text-2xl" title="Ask Peter about XPUB">Your wallet</h2>
    <div class="alert alert-info shadow-lg">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>We strongly suggest you use a separate wallet for Plebeian Market only!</span>
        </div>
    </div>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <input bind:value={xpub} id="xpub" name="xpub" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    {#if saveButtonActive}
        <div id="save-profile" class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>
