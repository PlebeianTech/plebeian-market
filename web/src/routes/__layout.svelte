<script lang="ts">
    import "../app.css";
    import { onMount } from 'svelte';
    import { fetchAPI } from "../api";
    import { token, ContributionPercent, TwitterUsername, TwitterUsernameVerified } from "../stores";
    import Navbar from "../Navbar.svelte";

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

    token.set(localStorage.getItem('token'));

    if ($token && !$TwitterUsername) {
        fetchProfile();
    }
</script>

<div class="flex flex-col">
  <Navbar />
  <slot />
</div>
