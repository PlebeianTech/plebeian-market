<script lang="ts">
    import { onDestroy } from "svelte";
    import { ErrorHandler, postProfile, putVerifyTwitter } from "../services/api";
    import { token, user, Info } from "../stores";
    import V4V from "./V4V.svelte";

    let twitterUsername;
    let contributionPercent;

    let invalidTwitterUsername = false;

    let twitterUsernameVerificationTweet;

    function isTwitterUsernameValid() {
        return !(twitterUsername === null || twitterUsername.length === 0);
    }

    let saving = false;
    function save() {
        if (document.getElementById('save-profile')!.classList.contains("disabled")) {
            return;
        }
        invalidTwitterUsername = !isTwitterUsernameValid();
        if (invalidTwitterUsername) {
            return;
        }

        saving = true;

        postProfile($token, {twitterUsername, contributionPercent},
            u => {
                saving = false;

                user.set(u);
                Info.set("Your profile has been saved!");

                hide();

                if (!u.twitterUsernameVerified
                    && u.twitterUsernameVerificationTweet !== null
                    && localStorage.getItem('initial-login-seller') === null) {
                    /* NB: if you log in from the home page without having a Twitter username set (ie. initial-login-seller is set)
                    we don't want to ask for Twitter verification at this point, since you'll get verified when starting an auction */
                    showTwitterVerification(u.twitterUsernameVerificationTweet);
                }
            },
            new ErrorHandler(true, () => saving = false));
    }

    export function show() {
        if (!$user) {
            return;
        }

        twitterUsername = $user.twitterUsername ? `${$user.twitterUsername}` : "";
        contributionPercent = $user.contributionPercent;

        if ($user.hasAuctions && contributionPercent === null) {
            contributionPercent = 3; // default value
        }

        let toggle = <HTMLInputElement>document.getElementById('profile-modal-toggle');
        if (toggle) {
            toggle.checked = true;
        }
    }

    export function showIfIncomplete() {
        if (!$user) {
            return;
        }

        if ($user.twitterUsername === null || $user.twitterUsername.length === 0) {
            show();
        }

        if ($user.hasAuctions && $user.contributionPercent === null) {
            show();
        }
    }

    function hide() {
        let toggle = <HTMLInputElement>document.getElementById('profile-modal-toggle');
        if (toggle) {
            toggle.checked = false;
        }
    }

    function showTwitterVerification(tweetUrl: string) {
        twitterUsernameVerificationTweet = tweetUrl;
        let toggle = <HTMLInputElement>document.getElementById('twitter-verification-modal-toggle');
        if (toggle) {
            toggle.checked = true;
        }
    }

    function hideTwitterVerification() {
        let toggle = <HTMLInputElement>document.getElementById('twitter-verification-modal-toggle');
        if (toggle) {
            toggle.checked = false;
        }
    }

    let verifying = false;
    function verifyTwitter() {
        verifying = true;
        putVerifyTwitter($token,
            () => {
                verifying = false;
                user.update(u => { if (u) { u.twitterUsernameVerified = true; } return u; });
                Info.set("Your Twitter account has been verified!");
                hideTwitterVerification();
            },
            new ErrorHandler(true, () => verifying = false));
    }

    const unsubscribe = user.subscribe(value => {
        showIfIncomplete();
    });

    onDestroy(unsubscribe);
</script>

<input type="checkbox" id="profile-modal-toggle" for="profile-modal" class="modal-toggle" />
<div class="modal">
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-1xl">
        {#if $user && $user.twitterUsername && (!$user.hasAuctions || $user.contributionPercent !== null)}
            <label for="profile-modal" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={hide}>✕</label>
        {/if}
        <div class="w-full">
            {#if !($user && $user.twitterUsername)}
            <div class="alert alert-info shadow-lg">
                <div>
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <span>We use your Twitter account to start the auctions. We DO NOT collect any personal information.</span>
                </div>
            </div>
            {/if}
            <div class="w-full flex items-center justify-center">
                <div class="form-control w-full max-w-lg">
                    <label class="label" for="twitter-username">
                        <span class="label-text">Twitter username</span>
                    </label>
                    <div class="z-0 translate-y-9 translate-x-2">
                        <span>@</span>
                    </div>
                    <input bind:value={twitterUsername} id="twitter-username" name="twitter-username" type="text" class:input-error={invalidTwitterUsername && !isTwitterUsernameValid()} class="bg-transparent z-10 ml-1.5 input input-bordered w-full max-w-xs" />
                </div>
            </div>

            {#if $user && $user.hasAuctions}
                <V4V bind:contributionPercent />
            {/if}

            <div class="flex justify-center items-center mt-4 h-15">
                {#if !$user || saving || ((twitterUsername === $user.twitterUsername) && (contributionPercent === $user.contributionPercent))}
                    <button class="btn" disabled>Save</button>
                {:else}
                    <div id="save-profile" class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
                {/if}
            </div>
        </div>
    </div>
</div>

<input type="checkbox" id="twitter-verification-modal-toggle" for="twitter-verification-modal" class="modal-toggle" />
<div class="modal">
    <div class="modal-box relative flex justify-center items-center">
        <label for="twitter-verification-modal" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={hideTwitterVerification}>✕</label>
        <div class="w-full">
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
                {#if verifying}
                    <button class="btn" disabled>Verify</button>
                {:else}
                    <div id="verify-twitter" class="glowbutton glowbutton-verify" on:click|preventDefault={verifyTwitter}></div>
                {/if}
            </div>
        </div>
    </div>
</div>