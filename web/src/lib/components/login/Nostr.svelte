<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { ErrorHandler, loginNostr } from "$lib/services/api";
    import type { User } from "$lib/types/user";
    import { token, user, Info } from "$lib/stores";

    const dispatch = createEventDispatcher();

    export let onLogin: (user: User | null) => void = (_) => {};

    enum Step {
        SetKey,
        SetVerificationPhrase,
    }

    let step: Step;

    let npub: string | null = null;
    let verificationPhrase: string | null = null;

    function sendVerificationPhrase() {
        if (npub === null) {
            return;
        }

        loginNostr(npub, null,
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
        loginNostr(npub, verificationPhrase, () => verifying = false,
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

{#if step === Step.SetKey}
    <div class="w-full flex items-center justify-center mt-4">
        <div class="form-control w-full max-w-full">
            <label class="label" for="npub">
                <span class="label-text">Your NPUB</span>
            </label>
            <input bind:value={npub} type="text" name="npub" class="input input-lg input-bordered" />
        </div>
    </div>
    <div class="w-full flex items-center justify-center mt-4">
        <button class="btn btn-primary" on:click={sendVerificationPhrase}>Continue</button>
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