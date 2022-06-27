<script lang="ts">
    import { onDestroy } from "svelte";
    import { postProfile } from "../services/api";
    import { token, user, Info } from "../stores";
    import V4V from "./V4V.svelte";

    let twitterUsername;
    let contributionPercent;

    let invalidTwitterUsername = false;

    function isTwitterUsernameValid() {
        return !(twitterUsername === null || twitterUsername.length === 0);
    }

    function save() {
        if (document.getElementById('save-profile')!.classList.contains("disabled")) {
            return;
        }
        invalidTwitterUsername = !isTwitterUsernameValid();
        if (invalidTwitterUsername) {
            return;
        }

        postProfile($token, {twitterUsername, contributionPercent},
            u => {
                user.set(u);
                Info.set("Your profile has been saved!");
                hide();
            });
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
                {#if !$user || ((twitterUsername === $user.twitterUsername) && (contributionPercent === $user.contributionPercent))}
                    <button class="btn" disabled>Save</button>
                {:else}
                    <div id="save-profile" class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
                {/if}
            </div>
        </div>
    </div>
</div>