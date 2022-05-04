<script>
    import { onDestroy } from 'svelte';
    import { fetchAPI } from "../common.js";
    import { token, ContributionPercent, TwitterUsername } from "../stores.js";
    import Loading from "../Loading.svelte";
    import Login from "../Login.svelte";
    import About from "./About.svelte";
    import Auctions from "./Auctions.svelte";
    import Navbar from "../Navbar.svelte";
    import Profile from "../Profile.svelte";

    let isLoading = false;

    let selected = 'app';

    function onSelect(key) {
        if (key === 'logout') {
            token.set(null);
            selected = 'app';
        } else {
            selected = key;
        }
    }

    const unsubscribe = token.subscribe(tokenValue => {
        if (!tokenValue) {
            return;
        }
        isLoading = true;
        fetchAPI("/users/me", 'GET', tokenValue, null,
            (response) => {
                isLoading = false;
                if (response.status === 200) {
                    response.json().then(data => {
                        ContributionPercent.set(data.user.contribution_percent);
                        TwitterUsername.set(data.user.twitter_username);
                    });
                }
            });
    });
	onDestroy(unsubscribe);

    token.set(sessionStorage.getItem('token'));
</script>

<div class="flex flex-col">
    <Navbar onSelect={onSelect} />

    {#if selected === 'about'}
        <About />
    {:else if selected === 'app'}
        {#if $token === null}
            <Login />
        {:else}
            {#if isLoading}
                <Loading />
            {:else}
                {#if $ContributionPercent === null}
                    <Profile />
                {:else}
                    <Auctions />
                {/if}
            {/if}
        {/if}
    {:else if selected === 'profile'}
        <Profile onSave={() => selected = 'app'} />
    {/if}
</div>
