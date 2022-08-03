<script lang="ts">
    import { token, user, Info } from "$lib/stores";
    import { ErrorHandler, putVerifyTwitter } from "$lib/services/api";

    export let onSave: () => void = () => {};

    $: twitterUsernameVerificationTweet = $user ? $user.twitterUsernameVerificationTweet : null;

    $: verifyButtonActive = !verifying;

    let verifying = false;
    function verify() {
        verifying = true;
        putVerifyTwitter($token,
            () => {
                user.update(u => { if (u) { u.twitter.usernameVerified = true; } return u; });
                Info.set("Your Twitter account has been verified!");
                verifying = false;
                onSave();
            },
            new ErrorHandler(true, () => verifying = false));
    }
</script>

<div class="alert alert-info shadow-lg">
    <div>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span>Please like the tweet below to verify your profile.</span>
    </div>
</div>
<div class="w-full flex items-center justify-center mt-4">
    <div class="form-control w-full max-w-lg">
        <a class="btn btn-primary" href="{twitterUsernameVerificationTweet}" target="_blank">Open Twitter</a>
    </div>
</div>
<div class="flex justify-center items-center mt-4 h-24">
    {#if verifyButtonActive}
        <div id="verify-twitter" class="glowbutton glowbutton-verify" on:click|preventDefault={verify}></div>
    {:else}
        <button class="btn" disabled>Verify</button>
    {/if}
</div>