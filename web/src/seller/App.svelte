<script>
    import { onDestroy } from 'svelte';
    import { fetchAPI } from "../common.js";
    import { token, ContributionPercent, TwitterUsername } from "../stores.js";
    import Loading from "../Loading.svelte";
    import Login from "../Login.svelte";
    import About from "./About.svelte";
    import Auctions from "./Auctions.svelte";
    import Profile from "../Profile.svelte";

    let isLoading = false;

    let selected = 'app';

    function logout() {
        token.set(null);
        selected = 'app';
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
    <nav class="bg-white dark:bg-slate-900 px-2 sm:px-4 py-2.5 rounded">
        <div class="container flex flex-wrap justify-between items-center mx-auto">
            <span class="flex items-center">
                <img src="/static/images/logo.jpg" class="mr-3 h-6 sm:h-9 rounded" alt="Plebeian Logo" />
                <span class="self-center text-xl font-semibold whitespace-nowrap dark:text-white">Plebeian Market</span>
            </span>
            <span class="w-full md:block md:w-auto">
                <span class="flex flex-col mt-4 md:flex-row md:space-x-8 md:mt-0 md:text-sm md:font-medium">
                    <span>
                        <a href={null} on:click={() => selected = 'app'} class="h-full block pr-4 pl-3 flex justify-center items-center {selected === 'app' ? 'selected-menu-item' : 'menu-item'}" aria-current="page">Home</a>
                    </span>
                    <span>
                        <a href={null} on:click={() => selected = 'about'} class="h-full block pr-4 pl-3 flex justify-center items-center {selected === 'about' ? 'selected-menu-item' : 'menu-item'}">About</a>
                    </span>
                    <span class="flex items-center">
                        {#if $token}
                        <span class="dropdown dropdown-end">
                            <button tabindex="0" type="button" class="btn flex mr-3 text-sm bg-gray-800 rounded-full md:mr-0 focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600">
                                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
                                <svg class="hidden w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                            </button>
                                <ul tabindex="0" class="p-2 dropdown-content menu rounded-box shadow bg-base-100 w-52">
                                    <li>
                                        <a href={null} on:click|preventDefault={() => selected = 'profile'} class="cursor-pointer block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Profile</a>
                                    </li>
                                    <li>
                                        <a href={null} on:click|preventDefault={logout} class="cursor-pointer block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Log out</a>
                                    </li>
                                </ul>
                        </span>
                        {/if}
                    </span>
                </span>
            </span>
        </div>
    </nav>

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
