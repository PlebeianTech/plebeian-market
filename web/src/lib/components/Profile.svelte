<script lang="ts">
    import { fetchAPI } from "../services/api";
    import { token, ContributionPercent, TwitterUsername, TwitterUsernameVerified, Info } from "../stores";

    let contributionPercentValue = $ContributionPercent || 3;

    let invalidTwitterUsername = false;

    function isTwitterUsernameValid() {
        return !($TwitterUsername === null || $TwitterUsername.length === 0);
    }

    export function fetch() {
        fetchAPI("/users/me", 'GET', $token, null,
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        ContributionPercent.set(data.user.contribution_percent);
                        TwitterUsername.set(data.user.twitter_username);
                        TwitterUsernameVerified.set(data.user.twitter_username_verified);

                        if (!$TwitterUsername) {
                            show();
                        }
                    });
                }
            });
    }

    function save() {
        invalidTwitterUsername = !isTwitterUsernameValid();
        if (invalidTwitterUsername) {
            return;
        }
        const data = {twitter_username: $TwitterUsername, contribution_percent: contributionPercentValue};
        fetchAPI("/users/me", 'POST', $token, JSON.stringify(data),
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        ContributionPercent.set(data.user.contribution_percent);
                        TwitterUsername.set(data.user.twitter_username);
                        Info.set("Your profile has been saved!");
                        hide();
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

    function hide() {
        let toggle = <HTMLInputElement>document.getElementById('profile-modal-toggle');
        if (toggle) {
            toggle.checked = false;
            fetch(); // re-fetch the profile because the stores have already been modified by binding
        }
    }
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
        <label for="profile-modal" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={hide}>✕</label>
        <div class="w-1/2">
            <div class="form-group mt-3">
                <input id="twitter-username" name="twitter-username" class:invalid-field={invalidTwitterUsername && !isTwitterUsernameValid()} class="form-field" bind:value={$TwitterUsername} />
                <label class:invalid={invalidTwitterUsername && !isTwitterUsernameValid()} class="form-label" for="twitter-username">Twitter username</label>
            </div>

            <h3 class="text-2xl text-center mt-10">Your Value4Value contribution (percent)</h3>
            <div class="pt-5">
                <input type="range" min="0" max="5" bind:value={contributionPercentValue} class="range" step="0.5" />
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
                { contributionPercentValue }%
            </div>

            <div class="text-4xl text-center">
                {#if contributionPercentValue === 0}
                    {@html "&#x1F4A9;"}
                {:else if contributionPercentValue < 2}
                    {@html "&#x1F625;"}
                {:else if contributionPercentValue < 3}
                    {@html "&#x1F615;"}
                {:else if contributionPercentValue < 4}
                    {@html "&#x1F610;"}
                {:else if contributionPercentValue <= 4.5}
                    {@html "&#x1F642;"}
                {:else if contributionPercentValue <= 5}
                    {@html "&#x1F60D;"}
                {/if}
            </div>

            <div class="flex justify-center items-center mt-4">
                <div class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
            </div>
        </div>
    </div>
</div>