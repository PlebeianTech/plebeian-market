<svelte:head>
    <script src="https://unpkg.com/@popperjs/core@2" on:load={popperLoaded}></script>
</svelte:head>

<script>
    import { onMount } from 'svelte';
    import { fetchAPI, token, ContributionPercent, Nym, TwitterUsername } from "../common.js";
    import Loading from '../Loading.svelte';
    import Login from '../Login.svelte';
    import About from './About.svelte';
    import Auctions from './Auctions.svelte';
    import Profile from '../Profile.svelte';

    $token = sessionStorage.getItem('token');

    let isLoading = false;

    if ($token) {
        isLoading = true;
        fetchAPI("/users/me", 'GET', $token, null,
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        ContributionPercent.set(data.user.contribution_percent);
                        Nym.set(data.user.nym);
                        TwitterUsername.set(data.user.twitter_username);
                        isLoading = false;
                    });
                }
            });
    }

    let selected = 'app';

    function logout() {
        $token = null;
        selected = 'app';
    }

    let popperReady = false;
    let mounted = false;
    let popperInitialized = false;

    onMount(() => {
        mounted = true;
        if (popperReady) {
            initPopper();
        }
    });

    function popperLoaded() {
        popperReady = true;
        if (mounted) {
            initPopper();
        }
    }

    function initPopper() {
        const button = document.getElementById('dropdown-trigger');
        const tooltip = document.getElementById('dropdown');

        var popper = Popper.createPopper(button, tooltip, {placement: 'bottom-end'});

        button.addEventListener('click', () => {
            tooltip.style.display = tooltip.style.display === 'block' ? 'none' : 'block';
            popper.update();
        });

        popperInitialized = true;
    }

    function contains(parent, child) {
        return parent !== child && parent.contains(child);
    }

    function click(e) {
        if (!contains(document.getElementById('dropdown-trigger'), e.target)) {
            document.getElementById('dropdown').style.display = 'none';
        }
    }
</script>

<svelte:window on:click={click} />

<style>
    #dropdown {
        display: none;
    }
</style>

<div class="flex flex-col">
    <nav class="bg-white dark:bg-slate-900 px-2 sm:px-4 py-2.5 rounded">
        <div class="container flex flex-wrap justify-between items-center mx-auto">
            <span class="flex items-center">
                <img src="/static/images/logo.jpg" class="mr-3 h-6 sm:h-9 rounded" alt="Plebeian Logo" />
                <span class="self-center text-xl font-semibold whitespace-nowrap dark:text-white">Plebeian Market</span>
            </span>
            <div class="w-full md:block md:w-auto">
                <ul class="flex flex-col mt-4 md:flex-row md:space-x-8 md:mt-0 md:text-sm md:font-medium">
                    <li>
                        <a href={null} on:click={() => selected = 'app'} class="block py-2 pr-4 pl-3 {selected === 'app' ? 'selected-menu-item' : 'menu-item'}" aria-current="page">Home</a>
                    </li>
                    <li>
                        <a href={null} on:click={() => selected = 'about'} class="block py-2 pr-4 pl-3 {selected === 'about' ? 'selected-menu-item' : 'menu-item'}">About</a>
                    </li>
                    <div class="flex items-center">
                        <button type="button" class="flex mr-3 text-sm bg-gray-800 rounded-full md:mr-0 focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600" aria-expanded="false" id="dropdown-trigger">
                            <span class="sr-only">Open user menu</span>
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
                            <svg class="hidden w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                        </button>
                        <!-- Dropdown menu -->
                        <div class="z-50 my-4 text-base list-none bg-white rounded divide-y divide-gray-100 shadow dark:bg-gray-700 dark:divide-gray-600" id="dropdown">
                            <ul class="py-1" aria-labelledby="dropdown">
                                {#if $token}
                                <li>
                                    <a href={null} on:click|preventDefault={() => selected = 'profile'} class="cursor-pointer block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Profile</a>
                                </li>
                                <li>
                                    <a href={null} on:click|preventDefault={logout} class="cursor-pointer block py-2 px-4 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">Log out</a>
                                </li>
                                {/if}
                            </ul>
                        </div>
                    </div>
                </ul>
            </div>
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
