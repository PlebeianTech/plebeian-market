<script lang="ts">
    import { onMount } from 'svelte';
    import { hasExtension, encodeNpub } from "$lib/nostr/utils";
    import { ErrorHandler, putProfile, putVerify } from "$lib/services/api";
    import { user, token, Info } from "$lib/stores";
    import { ExternalAccountProvider } from "$lib/types/user";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";

    export let onSave: () => void = () => {};

    let nostrPublicKey: string = "";
    let nostrPublicKeyVerified: boolean = false;

    $: isValidInput = nostrPublicKey !== null && nostrPublicKey !== "";
    $: saveButtonActive = $user && isValidInput && !inRequest && nostrPublicKey !== $user.nostrPublicKey;

    let inRequest = false;

    async function getKeyFromExtension() {
        let pubkey = await (window as any).nostr.getPublicKey();
        nostrPublicKey = encodeNpub(pubkey);
    }

    function save() {
        if (nostrPublicKey === null) {
            return;
        }
        inRequest = true;
        putProfile($token, {nostrPublicKey},
            u => {
                user.set(u);
                Info.set("Your Nostr public key has been saved!");
                inRequest = false;
                onSave();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    let phrase: string = "";

    function verify() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Nostr, false, phrase,
            () => {
                user.update(u => { if (u) { u.nostrPublicKeyVerified = true; } return u; });
                Info.set("Your Nostr key has been verified!");
                inRequest = false;
                onSave();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    function resend() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Nostr, true, undefined,
            () => {
                user.update(u => { if (u) { u.nostrVerificationPhraseSentAt = new Date(); } return u; });
                Info.set("Check your Nostr DM!");
                inRequest = false;
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    onMount(async () => {
        if ($user) {
            nostrPublicKey = $user.nostrPublicKey || "";
            nostrPublicKeyVerified = $user.nostrPublicKeyVerified;
        }
    });
</script>

<div class="text-2xl breadcrumbs">
    <ul>
        <li>Settings</li>
        <li>Nostr</li>
    </ul>
</div>

{#if $user}
    {#if $user.nostrPublicKey && $user.nostrPublicKeyVerified && $user.nostrPublicKey === nostrPublicKey}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl">Your verified Nostr public key is:</div>
                <div class="flex justify-center items-center gap-4">
                    <pre class="my-8 text-lg bg-base-300 text-center">{$user.nostrPublicKey}</pre>
                    <button class="btn btn-secondary" on:click={() => nostrPublicKey = ""}>Change</button>
                </div>
                <div>You can use any Nostr client that supports encrypted direct messages (NIP-04) to log in to the Plebeian Market backend.</div>
            </div>
        </div>
    {:else}
        <div class="w-full flex items-center justify-center mt-8">
            <div class="form-control w-full max-w-lg">
                <input bind:value={nostrPublicKey} id="nostr-public-key" name="nostr-public-key" type="text" class="bg-transparent z-10 ml-1.5 input input-bordered input-md w-full" />
            </div>
        </div>
        <div class="w-full flex items-center justify-center mt-4 gap-5">
            {#if hasExtension()}
                <button class="btn" class:btn-primary={nostrPublicKey === null} class:btn-secondary={nostrPublicKey !== null} on:click={getKeyFromExtension}>Get from extension</button>
            {/if}
        </div>

        <div class="flex justify-center items-center mt-4 h-15">
            {#if saveButtonActive}
                <button id="save-profile" class="btn btn-primary" on:click|preventDefault={save}>Save</button>
            {:else}
                <button class="btn" disabled>Save</button>
            {/if}
        </div>
    {/if}
    {#if $user.nostrPublicKey && !$user.nostrPublicKeyVerified}
        <div class="mt-4">
            {#if $user && !$user.nostrVerificationPhraseSentAt}
                <InfoBox>
                    <span>We will send the verification phrase over encrypted DM.</span>
                </InfoBox>
                <div class="w-full flex items-center justify-center mt-4">
                    <div class="form-control w-full max-w-lg">
                        <button class="btn btn-primary" on:click={resend} disabled={inRequest}>Send</button>
                    </div>
                </div>
            {:else}
                <InfoBox>
                    <span>Please enter the three BIP-39 words we sent to you over Nostr DM.</span>
                </InfoBox>
                <div class="w-full flex items-center justify-center mt-4">
                    <div class="form-control w-full max-w-full">
                        <label class="label" for="title">
                            <span class="label-text">Verification phrase</span>
                        </label>
                        <input bind:value={phrase} type="text" name="phrase" class="input input-lg input-bordered" />
                    </div>
                </div>
                <div class="flex justify-center items-center mt-4 h-24 gap-5">
                    {#if !inRequest}
                        <button id="verify-nostr" class="btn btn-primary" on:click|preventDefault={verify}>Verify</button>
                    {:else}
                        <button class="btn" disabled>Verify</button>
                    {/if}
                    <button class="btn" on:click={resend} disabled={inRequest}>Resend</button>
                </div>
            {/if}
        </div>
    {/if}
{/if}
