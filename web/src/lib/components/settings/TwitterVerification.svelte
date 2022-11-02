<script lang="ts">
    import { token, user, Info } from "$lib/stores";
    import { ErrorHandler, putVerifyTwitter } from "$lib/services/api";

    let phrase: string = "";

    export let onSave: () => void = () => {};

    let inRequest = false;

    function verify() {
        inRequest = true;
        putVerifyTwitter($token, false, phrase,
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
        putVerifyTwitter($token, true, undefined,
            () => {
                Info.set("Check your Twitter DM!");
                inRequest = false;
            },
            new ErrorHandler(true, () => inRequest = false));
    }
</script>

<div class="w-full flex items-center justify-center mt-4">
    <div class="form-control w-full max-w-full">
        <label class="label" for="title">
            <span class="label-text">Phrase</span>
        </label>
        <input bind:value={phrase} type="text" name="phrase" class="input input-lg input-bordered" />
    </div>
</div>
<div class="flex justify-center items-center mt-4 h-24">
    {#if !inRequest}
        <div id="verify-twitter" class="glowbutton glowbutton-verify" on:click|preventDefault={verify}></div>
    {:else}
        <button class="btn" disabled>Verify</button>
    {/if}
</div>
<div class="divider"></div>
<div class="w-full flex items-center justify-center mt-4">
    <div class="form-control w-full max-w-lg">
        <button class="btn btn-primary" on:click={resend} disabled={inRequest}>Resend</button>
    </div>
</div>