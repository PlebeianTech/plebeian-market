<script>
    import { token } from "../common.js";
    import Login from '../Login.svelte';
    import About from './About.svelte';
    import Auctions from './Auctions.svelte';

    $token = sessionStorage.getItem('token');

    let selected = 'app';

    function logout() {
        $token = null;
    }
</script>

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
                    {#if $token}
                    <li>
                        <a href="{null}" class="menu-item" on:click|preventDefault={logout}>Log out</a>
                    </li>
                    {/if}
                </ul>
            </div>
        </div>
    </nav>
    <div class="pt-10 flex justify-center items-center">
        {#if selected === 'about'}
            <About />
        {:else if selected === 'app'}
            {#if $token}
                <Auctions />
            {:else}
                <Login />
            {/if}
        {/if}
    </div>
</div>
