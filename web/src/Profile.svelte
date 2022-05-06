<script>
    import { goto } from "$app/navigation";
    import Slider from "@bulatdashiev/svelte-slider";
    import { fetchAPI } from "./common.js";
    import { intent, token, ContributionPercent, TwitterUsername } from "./stores.js";

    let value = $ContributionPercent !== null ? [$ContributionPercent, $ContributionPercent] : [10, 10];

    let twitterUsernameValue = $TwitterUsername;
    let invalidTwitterUsername = false;

    function isTwitterUsernameValid() {
        return !(twitterUsernameValue === null || twitterUsernameValue.length === 0);
    }

    function saveProfile() {
        invalidTwitterUsername = !isTwitterUsernameValid();
        if (invalidTwitterUsername) {
            return;
        }
        const data = {twitter_username: twitterUsernameValue, contribution_percent: value[0]};
        fetchAPI("/users/me", 'POST', $token, JSON.stringify(data),
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        ContributionPercent.set(data.user.contribution_percent);
                        TwitterUsername.set(data.user.twitter_username);
                        goto($intent === "seller" ? "/auctions" : `/auctions/${$intent}`);
                    });
                }
            });
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

<div class="flex justify-center items-center">

    <div class="w-1/2">
        <div class="form-group">
            <input id="twitter-username" name="twitter-username" class:invalid-field={invalidTwitterUsername && !isTwitterUsernameValid()} class="form-field" bind:value={twitterUsernameValue} />
            <label class:invalid={invalidTwitterUsername && !isTwitterUsernameValid()} class="form-label" for="twitter-username">Twitter username</label>
        </div>

        <h3 class="text-zinc-300 text-3xl text-center mt-10">Your Value4Value contribution (percent)</h3>
        <div class="pt-5">
            <Slider min="0" max="5" step="0.5" bind:value />
        </div>

        <div class="text-2xl text-zinc-300 text-center">
            { value[0] }
        </div>

        <div class="text-4xl text-center">
            {#if value[0] === 0}
                {@html "&#x1F4A9;"}
            {:else if value[0] < 2}
                {@html "&#x1F625;"}
            {:else if value[0] < 3}
                {@html "&#x1F615;"}
            {:else if value[0] < 4}
                {@html "&#x1F610;"}
            {:else if value[0] <= 4.5}
                {@html "&#x1F642;"}
            {:else if value[0] <= 5}
                {@html "&#x1F60D;"}
            {/if}
        </div>

        <div class="flex justify-center items-center mt-4">
            <div class="glowbutton glowbutton-save" on:click|preventDefault={saveProfile}></div>
        </div>
    </div>
</div>