<script>
    import { fetchAPI, token, Nym, TwitterUsername } from "../common.js";

    let nymValue = $Nym;
    let twitterUsernameValue = $TwitterUsername;

    export let onSave = () => {};

    function saveProfile() {
        if (!nymValue || !twitterUsernameValue) {
            return;
        }
        fetchAPI("/users/me", 'POST', $token,
            JSON.stringify({nym: nymValue, twitter_username: twitterUsernameValue}),
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        Nym.set(data.user.nym);
                        TwitterUsername.set(data.user.twitter_username);
                        onSave();
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

<div class="form-group">
    <input id="nym" name="nym" class:invalid-field={!nymValue || nymValue === ''} class="form-field" bind:value={nymValue} />
    <label class:invalid={!nymValue || nymValue === ''} class="form-label" for="nym">Nym</label>
</div>

<div class="form-group">
    <input id="twitter-username" name="twitter-username" class:invalid-field={!twitterUsernameValue || twitterUsernameValue === ''} class="form-field" bind:value={twitterUsernameValue} />
    <label class:invalid={!twitterUsernameValue || twitterUsernameValue === ''} class="form-label" for="twitter-username">Twitter username</label>
</div>

<div class="flex justify-center items-center">
    <div class="glowbutton glowbutton-save mt-2" on:click|preventDefault={saveProfile}></div>
</div>