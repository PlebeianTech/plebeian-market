<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { ErrorHandler, nostrAuth } from "$lib/services/api";
    import type { User } from "$lib/types/user";
    import { token, user, Info, Error, AuthBehavior } from "$lib/stores";
    import { getKeyFromKeyOrNpub, hasExtension } from '$lib/nostr/utils';
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

    let key: string | null = null;
    let verificationPhrase: string | null = null;

    async function getKeyFromExtension() {
        key = await (window as any).nostr.getPublicKey();
    }

    function sendVerificationPhrase() {
        if (key === null) {
            return;
        }

        let cleanKey = getKeyFromKeyOrNpub(key);

        if (cleanKey === null) {
            Error.set("Invalid npub!");
            return;
        }

        nostrAuth(behavior, cleanKey, null,
            () => {
                Info.set("Sent the verification phrase!");
                step = Step.SetVerificationPhrase;
            });
    }

    let verifying = false;
    function verify() {
        if (key === null || verificationPhrase === null) {
            return;
        }

        let cleanKey = getKeyFromKeyOrNpub(key);

        if (cleanKey === null) {
            Error.set("Invalid npub!");
            return;
        }

        verifying = true;
        nostrAuth(behavior, cleanKey, verificationPhrase, () => verifying = false,
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
                    Your verification phrase: "IDENTIFY AS MYSELF"!
                </div>
            </ErrorBox>
        {/if}
        {#if step === Step.SetKey}
            <div class="w-full flex items-center justify-center mt-4">
                <div class="form-control w-full max-w-full">
                    <label class="label" for="key">
                        <span class="label-text">Your public key (HEX or NPUB formats accepted)</span>
                    </label>
                    <input bind:value={key} type="text" name="key" class="input input-lg input-bordered" />
                </div>
            </div>
            <div class="w-full flex items-center justify-center mt-4 gap-5">
                {#if key !== null && key !== ""}
                    <button class="btn btn-primary" on:click={sendVerificationPhrase}>Continue</button>
                {/if}
                {#if hasExtension()}
                    <button class="btn" class:btn-primary={key === null} class:btn-secondary={key !== null} on:click={getKeyFromExtension}>Get from extension</button>
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