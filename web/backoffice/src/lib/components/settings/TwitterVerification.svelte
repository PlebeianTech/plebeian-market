<script lang="ts">
    import { user, Info } from "$lib/stores";
    import { token } from "$sharedLib/stores";
    import { ErrorHandler, putVerify } from "$lib/services/api";
    import { ExternalAccountProvider } from "$lib/types/user";

    let phrase: string = "";

    export let onSave: () => void = () => {};

    let inRequest = false;

    function verify() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Twitter, false, phrase,
            () => {
                user.update(u => { if (u) { u.twitterUsernameVerified = true; } return u; });
                Info.set("Your Twitter account has been verified!");
                inRequest = false;
                onSave();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    function resend() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Twitter, true, undefined,
            () => {
                user.update(u => { if (u) { u.twitterVerificationPhraseSentAt = new Date(); } return u; });
                Info.set("Check your Twitter DM!");
                inRequest = false;
            },
            new ErrorHandler(true, () => inRequest = false));
    }
</script>

{#if $user}
    {#if !$user.twitterVerificationPhraseSentAt}
        <div class="alert alert-info shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>Please make sure your Twitter DMs are open and hit <strong>send</strong> below.</span>
        </div>
        <div class="w-full flex items-center justify-center mt-4">
            <div class="form-control w-full max-w-lg">
                <button class="btn btn-primary" on:click={resend} disabled={inRequest}>Send</button>
            </div>
        </div>
    {:else}
        <div class="alert alert-info shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>Please enter the three BIP-39 words we sent to your Twitter DMs.</span>
        </div>
        <div class="w-full flex items-center justify-center mt-4">
            <div class="form-control w-full max-w-full">
                <label class="label" for="title">
                    <span class="label-text">Verification phrase</span>
                </label>
                <input bind:value={phrase} type="text" name="phrase" class="input input-lg input-bordered" />
            </div>
        </div>
        <div class="flex justify-center items-center mt-4 h-24 gap-5">
            <button id="verify-twitter" class="btn btn-primary" class:btn-disabled={inRequest} on:click|preventDefault={verify}>Verify</button>
            <button class="btn" on:click={resend} disabled={inRequest}>Resend</button>
        </div>
    {/if}
{/if}
