<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { getKeyFromKeyOrNpub, hasExtension } from "$lib/nostr/utils";
    import { ErrorHandler, putProfile, putVerify, putVerifyLnurl, getProfile } from "$lib/services/api";
    import { user, token, Info, Error } from "$lib/stores";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";
    import Wallets from "$lib/components/notifications/Wallets.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import QR from "$lib/components/QR.svelte";
    import { ExternalAccountProvider } from "$lib/types/user";

    export let onSave: () => void = () => {};

    let hasLnauthKey: boolean = false;

    let lnurl;
    let qr;
    let k1: string | null = null;

    let inRequest = false;

    let checkTimeout: ReturnType<typeof setTimeout> | null = null;

    let nostrPublicKey: string = "";
    let nostrPublicKeyVerified: boolean = false;

    $: isValidInput = nostrPublicKey !== null && nostrPublicKey !== "";
    $: saveButtonActive = $user && isValidInput && !inRequest && nostrPublicKey !== $user.nostrPublicKey;

    async function getKeyFromExtension() {
        nostrPublicKey = await (window as any).nostr.getPublicKey();
    }

    function saveNostr() {
        if (nostrPublicKey === null) {
            return;
        }

        let cleanKey = getKeyFromKeyOrNpub(nostrPublicKey);

        if (cleanKey === null) {
            Error.set("Invalid npub!");
            return;
        }

        inRequest = true;
        putProfile($token, {nostrPublicKey: cleanKey},
            u => {
                user.set(u);
                Info.set("Your Nostr public key has been saved!");
                inRequest = false;
                onSave();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    let phrase: string = "";

    function verifyNostr() {
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

    function resendNostr() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Nostr, true, undefined,
            () => {
                user.update(u => { if (u) { u.nostrVerificationPhraseSentAt = new Date(); } return u; });
                Info.set("Check your Nostr DM!");
                inRequest = false;
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    function stopCheckingLnurl() {
        if (checkTimeout !== null) {
            clearTimeout(checkTimeout);
        }
    }

    function checkLnurl() {
        putVerifyLnurl($token, k1,
            (response) => {
                k1 = response.k1;
                lnurl = response.lnurl;
                qr = response.qr;
                checkTimeout = setTimeout(checkLnurl, 1000);
            },
            () => {
                checkTimeout = setTimeout(checkLnurl, 1000);
            },
            async () => {
                getProfile($token, 'me', u => {
                    user.set(u);
                    if ($user) {
                        hasLnauthKey = $user.hasLnauthKey;
                        if (hasLnauthKey) {
                            Info.set("Your Lightning wallet has been verified!");
                        }
                    }
                });
            },
            new ErrorHandler(true,
                (response) => {
                    if (response.status === 400 || response.status === 410) {
                        k1 = null;
                        checkTimeout = setTimeout(checkLnurl, 1000);
                    }
                }));
    }

    onMount(async () => {
        if ($user) {
            hasLnauthKey = $user.hasLnauthKey;

            nostrPublicKey = $user.nostrPublicKey || "";
            nostrPublicKeyVerified = $user.nostrPublicKeyVerified;
        }

        if (!hasLnauthKey) {
            checkLnurl();
        }
    });

    onDestroy(() => {
        stopCheckingLnurl();
    });
</script>

<div class="text-2xl breadcrumbs">
    <ul>
        <li>Settings</li>
        <li>Login</li>
    </ul>
</div>

{#if $user}
    <h2 class="text-3xl my-4">Lightning</h2>
    {#if $user.hasLnauthKey && hasLnauthKey}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl text-center">You have a Lightning wallet linked to your account.</div>
                <div class="flex justify-center items-center gap-4 my-8">
                    <button class="btn btn-secondary" on:click={() => { hasLnauthKey = false; k1 = null; checkLnurl(); }}>Change</button>
                </div>
                <div class="text-center">You can use that wallet to log in to the Plebeian Market backend.</div>
            </div>
        </div>
    {:else}
        {#if qr}
            <div>
                <Wallets />

                <QR qr={qr} protocol="lightning" address={lnurl} />
            </div>
        {:else}
            <Loading />
        {/if}
    {/if}

    <div class="divider"></div>

    <h2 class="text-3xl my-4">Nostr</h2>
    {#if $user.nostrPublicKey && $user.nostrPublicKeyVerified && $user.nostrPublicKey === nostrPublicKey}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl">Your verified Nostr public key is:</div>
                <div class="flex justify-center items-center gap-4">
                    <pre class="my-8 text-lg bg-base-300 text-center">{$user.nostrPublicKey}</pre>
                </div>
                <div class="flex justify-center items-center gap-4 my-8">
                    <button class="btn btn-secondary" on:click={() => nostrPublicKey = ""}>Change</button>
                </div>
                <div>You can use any Nostr client that supports encrypted direct messages (NIP-04) to log in to the Plebeian Market backend.</div>
            </div>
        </div>
    {:else}
        <div class="w-full flex items-center justify-center mt-8">
            <div class="form-control w-full max-w-lg">
                <label class="label" for="nostr-public-key">
                    <span class="label-text">Nostr public key (HEX or NPUB formats accepted)</span>
                </label>
                <input bind:value={nostrPublicKey} id="nostr-public-key" name="nostr-public-key" type="text" class="bg-transparent z-10 ml-1.5 input input-bordered input-md w-full" />
            </div>
        </div>
        <div class="w-full flex items-center justify-center mt-4 gap-5">
            {#if hasExtension()}
                <button class="btn" class:btn-primary={nostrPublicKey === null} class:btn-secondary={nostrPublicKey !== null} class:btn-disabled={inRequest} on:click={getKeyFromExtension}>Get from extension</button>
            {/if}
        </div>

        <div class="flex justify-center items-center mt-4 h-15">
            <button id="save-profile" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={saveNostr}>Save</button>
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
                        <button class="btn btn-primary" on:click={resendNostr} disabled={inRequest}>Send</button>
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
                    <button id="verify-nostr" class="btn btn-primary" class:btn-disabled={inRequest} on:click|preventDefault={verifyNostr}>Verify</button>
                    <button class="btn" on:click={resendNostr} disabled={inRequest}>Resend</button>
                </div>
            {/if}
        </div>
    {/if}
{/if}
