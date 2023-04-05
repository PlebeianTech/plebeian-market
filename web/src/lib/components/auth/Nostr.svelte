<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { ErrorHandler, nostrAuth } from "$lib/services/api";
    import type { User } from "$lib/types/user";
    import { token, user, Info, AuthBehavior } from "$lib/stores";
    import { hasExtension, encodeNpub } from '$lib/nostr/utils';
    import { isDevelopment } from "$lib/utils";
    import ErrorBox from "$lib/components/notifications/ErrorBox.svelte";

    const dispatch = createEventDispatcher();

    export let behavior: AuthBehavior;
    export let onLogin: (user: User | null) => void = (_) => {};

    enum Step {
        SetKey,
        SetVerificationPhrase,
    }

    let step: Step;

    let npub: string | null = null;
    let verificationPhrase: string | null = null;

    async function getKeyFromExtension() {
        let pubkey = await (window as any).nostr.getPublicKey();
        npub = encodeNpub(pubkey);
    }

    function sendVerificationPhrase() {
        if (npub === null) {
            return;
        }

        nostrAuth(behavior, npub, null,
            () => {
                Info.set("Sent the verification phrase!");
                step = Step.SetVerificationPhrase;
            });
    }

    let verifying = false;
    function verify() {
        if (npub === null || verificationPhrase === null) {
            return;
        }

        verifying = true;
        nostrAuth(behavior, npub, verificationPhrase, () => verifying = false,
            async (response) => {
                verifying = false;
                token.set(response.token);
                localStorage.setItem('token', response.token);
                dispatch('login', {})

                while ($user === null) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }

                onLogin(response.user);
            },
            new ErrorHandler(true, () => verifying = false));
    }

    onMount(() => {
        step = Step.SetKey;
    });
</script>

<div class="pb-48 pt-20 flex justify-center items-center">
    <div class="w-full">
        {#if isDevelopment()}
            <ErrorBox hasDetail={true}>
                <div>
                    You are in dev mode!
                </div>
                <div slot="detail">
                    We don't actually send DMs in dev mode, but rather they get printed in the terminal!
                </div>
            </ErrorBox>
        {/if}
        {#if step === Step.SetKey}
            <div class="w-full flex items-center justify-center mt-4">
                <div class="form-control w-full max-w-full">
                    <label class="label" for="npub">
                        <span class="label-text">Your NPUB</span>
                    </label>
                    <input bind:value={npub} type="text" name="npub" class="input input-lg input-bordered" />
                </div>
            </div>
            <div class="w-full flex items-center justify-center mt-4 gap-5">
                {#if npub !== null && npub !== ""}
                    <button class="btn btn-primary" on:click={sendVerificationPhrase}>Continue</button>
                {/if}
                {#if hasExtension()}
                    <button class="btn" class:btn-primary={npub === null} class:btn-secondary={npub !== null} on:click={getKeyFromExtension}>Get from extension</button>
                {/if}
            </div>
        {:else if step === Step.SetVerificationPhrase}
            <div class="w-full flex items-center justify-center mt-4">
                <div class="form-control w-full max-w-full">
                    <label class="label" for="verificationPhrase">
                        <span class="label-text">Verification phrase (check DM)</span>
                    </label>
                    <input bind:value={verificationPhrase} type="text" name="verificationPhrase" class="input input-lg input-bordered" />
                </div>
            </div>
            <div class="w-full flex items-center justify-center mt-4 gap-5">
                <button class="btn btn-primary" class:btn-disabled={verifying} on:click={verify}>Verify</button>
                <button class="btn btn-secondary" on:click={() => step = Step.SetKey}>Back</button>
                <button class="btn btn-secondary" on:click={sendVerificationPhrase}>Resend</button>
            </div>
        {/if}
    </div>
</div>