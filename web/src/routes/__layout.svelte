<script>
    import "../app.css";
    import { onMount } from 'svelte';
    import { fetchAPI } from "../common.js";
    import { token, ContributionPercent, TwitterUsername, TwitterUsernameVerified } from "../stores.js";
    import Navbar from "../Navbar.svelte";

    onMount(async () => {
        token.set(localStorage.getItem('token'));

        if ($token && !$TwitterUsername) {
            fetchProfile();
        }
    });

    function fetchProfile() {
        fetchAPI("/users/me", 'GET', $token, null,
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        ContributionPercent.set(data.user.contribution_percent);
                        TwitterUsername.set(data.user.twitter_username);
                        TwitterUsernameVerified.set(data.user.twitter_username_verified);
                    });
                }
            });
    }
</script>

<div class="flex flex-col">
  <Navbar />
  <slot />
</div>
