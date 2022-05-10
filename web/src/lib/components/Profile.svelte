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
        let toggle = <HTMLInputElement>document.getElementById('profile-modal-toggle');
        if (toggle) {
            toggle.checked = true;
        }
    }

    export function showIfIncomplete() {
        if (!$user) {
            return;
        }
        twitterUsername = $user.twitterUsername ? `${$user.twitterUsername}` : "";
        contributionPercent = $user.contributionPercent;
        if (!isTwitterUsernameValid()) {
            show();
        }
        if ($user.hasAuctions && contributionPercent === null) {
            contributionPercent = 3; // default value
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

<style>
    .invalid {
        color: #991B1B;
    }
    .invalid-field {
        border-bottom: 2px solid #991B1B;
    }
</style>

<input type="checkbox" id="profile-modal-toggle" for="profile-modal" class="modal-toggle" />
<div class="modal">
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-5xl">
        {#if $user && $user.twitterUsername && (!$user.hasAuctions || $user.contributionPercent !== null)}
            <label for="profile-modal" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={hide}>✕</label>
        {/if}
        <div class="w-1/2">
            <div class="form-group mt-3">
                <input id="twitter-username" name="twitter-username" class:invalid-field={invalidTwitterUsername && !isTwitterUsernameValid()} class="form-field" bind:value={twitterUsername} />
                <label class:invalid={invalidTwitterUsername && !isTwitterUsernameValid()} class="form-label" for="twitter-username">Twitter username</label>
            </div>

            {#if $user && $user.hasAuctions}
                <h3 class="text-2xl text-center mt-10">Your value4value donation</h3>
                <p class="text-center">Be a hero... save humanity</p>
                <p class="text-center">Your v4v donation goes a looooong way... it enables us to develop this service further and create more free open source solutions... 100% of your donation goes to powering the Bitcoin movement!</p>
                <div class="pt-5">
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
            {/if}

            <div class="flex justify-center items-center mt-4">
                <div id="save-profile" class:disabled={!$user || ((twitterUsername === $user.twitterUsername) && (contributionPercent === $user.contributionPercent))} class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
            </div>
        </div>
    </div>
</div>