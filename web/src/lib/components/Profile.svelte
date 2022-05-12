<script lang="ts">
    import { onDestroy } from "svelte";
    import { fetchAPI } from "../services/api";
    import { token, user, Info, Error } from "../stores";
    import { fromJson } from "../types/user";

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
        const data = {twitter_username: twitterUsername, contribution_percent: contributionPercent};
        fetchAPI("/users/me", 'POST', $token, JSON.stringify(data),
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        user.set(fromJson(data.user));
                        Info.set("Your profile has been saved!");
                        hide();
                    });
                } else {
                    response.json().then(data => {
                        Error.set(data.message);
                    });
                }
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

        if (!$user.twitterUsername === null) {
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
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-5xl">
        {#if $user && $user.twitterUsername && (!$user.hasAuctions || $user.contributionPercent !== null)}
            <label for="profile-modal" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={hide}>✕</label>
        {/if}
        <div class="w-full">
            <div class="w-full flex items-center justify-center">
                <div class="form-control w-full max-w-lg">
                    <label class="label" for="twitter-username">
                        <span class="label-text">Twitter username</span>
                    </label>
                    <input bind:value={twitterUsername} id="twitter-username" name="twitter-username" type="text" placeholder="@" class:input-error={invalidTwitterUsername && !isTwitterUsernameValid()} class="input input-bordered w-full max-w-xs" />
                </div>
            </div>
            {#if $user && $user.hasAuctions}
            <div class="flex items-center justify-center mt-8">
                <div>
                    <div class="form-control w-full max-w-lg">
                        <label class="label" for="contribution-percent">
                            <span class="label-text">Value4Value contribution</span>
                        </label>
                        <div>
                            <input type="range" min="0" max="5" bind:value={contributionPercent} class="range" step="0.5" />
                            <div class="w-full flex justify-between text-xs px-2">
                            <span>|</span>
                            <span>|</span>
                            <span>|</span>
                            <span>|</span>
                            <span>|</span>
                            <span>|</span>
                            </div>
                        </div>
                        <label class="label" for="contribution-percent">
                            <span class="label-text w-2/4">Generosity enables us to continue creating free and open source solutions!</span>
                            <span class="label-text text-right w-2/4">100% goes to powering the Bitcoin movement!</span>
                        </label>
                    </div>

                    <div class="text-2xl text-center">
                        { contributionPercent }%
                    </div>

                    <div class="text-4xl text-center">
                        {#if contributionPercent === 0}
                            {@html "&#x1F4A9;"}
                        {:else if contributionPercent < 2}
                            {@html "&#x1F625;"}
                        {:else if contributionPercent < 3}
                            {@html "&#x1F615;"}
                        {:else if contributionPercent < 4}
                            {@html "&#x1F610;"}
                        {:else if contributionPercent <= 4.5}
                            {@html "&#x1F642;"}
                        {:else if contributionPercent <= 5}
                            {@html "&#x1F60D;"}
                        {/if}
                    </div>
                </div>
            </div>
            {/if}

            <div class="flex justify-center items-center mt-4 h-24">
                {#if !$user || ((twitterUsername === $user.twitterUsername) && (contributionPercent === $user.contributionPercent))}
                    <button class="btn" disabled>Save</button>
                {:else}
                    <div id="save-profile" class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
                {/if}
            </div>
        </div>
    </div>
</div>