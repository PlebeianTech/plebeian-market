<script lang="ts">
    import { onMount } from 'svelte';
    import { afterNavigate } from "$app/navigation";
    import { getValue } from 'btc2fiat';
    import {BTC2USD} from "$lib/stores";
    import {NostrPublicKey, privateMessages, ShoppingCart} from "$sharedLib/stores";
    import {isProduction, getEnvironmentInfo, logout, requestLoginModal} from "$sharedLib/utils";
    import Modal from "$lib/components/Modal.svelte";
    import CompactShoppingCart from "$lib/components/stores/ShoppingCart.svelte";
    import ShoppingCartIcon from "$sharedLib/components/icons/ShoppingCart.svelte";
    import Settings from "$sharedLib/components/icons/Settings.svelte";
    import PrivateMessages from "$lib/components/nostr/PrivateMessages.svelte";
    import ProfilePicture from "$lib/components/nostr/ProfilePicture.svelte";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import User from "$sharedLib/components/icons/User.svelte";
    import World from "$sharedLib/components/icons/World.svelte";
    import Moon from "$sharedLib/components/icons/Moon.svelte";
    import Sun from "$sharedLib/components/icons/Sun.svelte";
    import Home from "$sharedLib/components/icons/Home.svelte";
    import Tools from "$sharedLib/components/icons/Tools.svelte";
    import Cash from "$sharedLib/components/icons/Cash.svelte";
    import Exit from "$sharedLib/components/icons/Exit.svelte";
    import Book from "$sharedLib/components/icons/Book.svelte";
    import Chat from "$sharedLib/components/icons/Chat.svelte";
    import Key from "$sharedLib/components/icons/Key.svelte";

    let modal: Modal | null;

    let prefersDark = false;

    let showMobileMenu = false;

    function toggleMobileMenu() {
        showMobileMenu = !showMobileMenu;

        document.body.style.overflow = showMobileMenu ? 'hidden' : '';
    }

    function hideMobileMenu() {
        showMobileMenu = false;

        document.body.style.overflow = '';
    }

    function toggleTheme() {
        let html = <HTMLHtmlElement>document.querySelector("html");

        if (!prefersDark) {
            html.dataset.theme = "dark";
            localStorage.theme = "dark";
        } else {
            html.dataset.theme = "light";
            localStorage.theme = "light";
        }
    }

    async function fetchFiatRate() {
        BTC2USD.set(await getValue());
    }

    onMount(async () => {
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            prefersDark = true;
        } else {
            prefersDark = false;
        }
    });

    afterNavigate(() => {
        hideMobileMenu();
    });
</script>

<nav class="fixed top-0 w-full backdrop-blur-3xl border-b border-gray-400/70 z-50" data-sveltekit-preload-data="hover">
    <div class="2xl:w-11/12 3xl:w-10/12 p-2 mx-auto lg:flex lg:flex-row flex-col md:justify-between md:items-center">
        <div class="flex items-center justify-between">
            <a href="/" class="flex items-center mr-2 indicator">
                <div class="flex items-center space-x-2">
                    <img src={"/images/logo.png"} class="mr-3 h-9 rounded" alt="Plebeian Technology" />
                    {#if !isProduction()}
                        <span class="indicator-item badge badge-error">{getEnvironmentInfo().substring(0,3)}</span>
                    {/if}
                    <h1 class="w-52 2xl:w-64 3xl:w-72 text-base lg:text-lg 2xl:text-xl font-bold hover:text-blue-400 duration-300">
                        Plebeian Market
                    </h1>

                </div>
            </a>

            <!-- LINKS -->
            <div class="lg:flex items-right w-full">
                <div class="hidden lg:flex">
                    <p>
                        <a href="/stalls" class="btn btn-ghost normal-case">Stall Browser</a>
                    </p>
                    <p>
                        <a href="/universe" class="btn btn-ghost normal-case">¡Universe!</a>
                    </p>
                    <p>
                        <a href="/marketsquare" class="btn btn-ghost normal-case">Market Square</a>
                    </p>
                    <p>
                        <a href="/skills" class="btn btn-ghost normal-case">Skills Market</a>
                    </p>
                    <p>
                        <a href="/orders" class="btn btn-ghost normal-case">Orders</a>
                    </p>
                    {#if $NostrPublicKey}
                        <p>
                            <a href="/p/{$NostrPublicKey}" class="btn btn-ghost normal-case"><b>Me</b></a>
                        </p>
                    {/if}
                    <p>
                        <a rel="external" href="/admin" class="btn btn-ghost normal-case">Stall Manager</a>
                    </p>
                    <p class="hidden xl:block">
                        {#if !$NostrPublicKey}
                            <a href={null} class="btn btn-ghost normal-case text-primary" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}><b>Login</b></a>
                        {:else}
                            <a href={null} class="btn btn-ghost normal-case" on:click={() => logout()} on:keypress={() => logout()}><b>Logout</b></a>
                        {/if}
                    </p>
                </div>
            </div>

            <!-- Mobile menu button -->
            <div on:click={toggleMobileMenu} on:keydown={toggleMobileMenu} class="lg:hidden flex justify-end p-2 -mr-3">
                <button type="button" class="text-black-800 dark:text-gray-200 focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                    </svg>
                </button>

                {#if $ShoppingCart.summary.totalQuantity || $privateMessages.unreadConversations}
                    <span class="indicator-item badge badge-sm badge-error -ml-3">
                        {Number($ShoppingCart.summary.totalQuantity ?? 0) + Number($privateMessages.unreadConversations ?? 0)}
                    </span>
                {/if}
            </div>
        </div>

        <div class:flex={showMobileMenu} class:hidden={!showMobileMenu} class="lg:flex lg:flex-row flex-col justify-center space-y-0">
            <div class="lg:flex items-center justify-start 2xl:space-x-2">
                <div class="float-right">
                    <label class="swap swap-rotate 2xl:mr-2" on:click={toggleTheme} on:keypress={toggleTheme}>
                        <input type="checkbox" bind:checked={prefersDark} />
                        <div class="swap-off w-9 h-9"><Sun /></div>
                        <div class="swap-on w-9 h-9"><Moon /></div>
                    </label>

                    <div class="btn btn-ghost btn-circle 2xl:mr-2">
                        <PrivateMessages />
                    </div>

                    <div class="dropdown dropdown-end ">
                        <label tabindex="0" class="btn btn-ghost btn-circle">
                            <div class="indicator">
                                <ShoppingCartIcon />
                                {#if $ShoppingCart.summary.totalQuantity}
                                    <span class="badge badge-sm badge-info indicator-item">{$ShoppingCart.summary.totalQuantity}</span>
                                {/if}
                            </div>
                        </label>
                        <div tabindex="0" class="mt-3 card card-compact card-bordered border-black dark:border-white dropdown-content w-fit bg-base-300 shadow-xl z-50">
                            <div class="card-body">
                                <CompactShoppingCart compact={true}></CompactShoppingCart>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="lg:dropdown lg:dropdown-end h-screen lg:h-fit clear-both" on:click={hideMobileMenu} on:keydown={hideMobileMenu}>
                    {#if $NostrPublicKey}
                        <ProfilePicture />
                    {:else}
                        <!-- Desktop menu button -->
                        <label class="btn btn-circle swap swap-rotate hidden md:grid">
                            <!-- this hidden checkbox controls the state -->
                            <input type="checkbox" />
                            <!-- hamburger icon -->
                            <svg class="swap-off fill-current w-8 h-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M64,384H448V341.33H64Zm0-106.67H448V234.67H64ZM64,128v42.67H448V128Z"/></svg>
                            <!-- close icon -->
                            <svg class="swap-on fill-current w-8 h-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><polygon points="400 145.49 366.51 112 256 222.51 145.49 112 112 145.49 222.51 256 112 366.51 145.49 400 256 289.49 366.51 400 400 366.51 289.49 256 400 145.49"/></svg>
                        </label>
                    {/if}

                    <ul role="menuitem" tabindex="0" class="float-right right-2 w-60 z-40 p-2 shadow menu menu-compact dropdown-content bg-base-300 text-accent-contend rounded-box md:border border-neutral-300">
                        {#if !$NostrPublicKey}
                            <li class="block md:hidden md:h-0 text-primary">
                                <a href={null} class="modal-button cursor-pointer text-base" on:click={() => {requestLoginModal(); hideMobileMenu()}} on:keypress={() => {requestLoginModal(); hideMobileMenu()}}>
                                    <span class="w-6 h-6 mr-1 stroke-primary"><Key /></span> <b>Login</b>
                                </a>
                            </li>
                        {/if}
                        <li class="block md:hidden md:h-0">
                            <a href="/" class="modal-button cursor-pointer text-base">
                                <span class="w-6 h-6 mr-1"><Home /></span> Home
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/stalls" class="modal-button cursor-pointer text-base">
                                <div class="w-6 h-6 mr-1"><Store /></div> Stall Browser
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/universe" class="modal-button cursor-pointer text-base">
                                <div class="w-6 h-6 mr-1"><World /></div> ¡Universe!
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/marketsquare" class="modal-button cursor-pointer text-base">
                                <div class="w-6 h-6 mr-1"><Chat /></div> Market Square
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/skills" class="modal-button cursor-pointer text-base">
                                <div class="w-6 h-6 mr-1"><Tools /></div> Skills Market
                            </a>
                        </li>
                        {#if $NostrPublicKey}
                            <li class="menu-title mt-2">
                                <span class="text-lg">Account</span>
                            </li>
                            <li class="block md:hidden md:h-0">
                                <a class="text-base" href="/p/{$NostrPublicKey}">
                                    <div class="w-6 h-6 mr-1"><User /></div> Me
                                </a>
                            </li>
                            <li class="block md:hidden md:h-0">
                                <a class="text-base" rel="external" href="/admin">
                                    <div class="w-6 h-6 mr-1"><Store /></div> Stall Manager
                                </a>
                            </li>
                            <li class="block md:hidden md:h-0">
                                <a class="text-base" href="/orders">
                                    <span class="w-6 h-6 mr-1"><Cash /></span> Orders
                                </a>
                            </li>
                            <li>
                                <a class="text-base" href="/settings">
                                    <span class="w-6 h-6 mr-1"><Settings /></span> Settings
                                </a>
                            </li>
                            <li>
                                <a href={null} on:click={() => {logout(); hideMobileMenu()}} class="modal-button cursor-pointer text-base">
                                    <span class="w-6 h-6 mr-1"><Exit /></span> Logout
                                </a>
                            </li>

                            <li class="menu-title mt-2 text-base">
                                <span class="text-lg">Other information</span>
                            </li>
                        {/if}

                        <li class="block md:hidden md:h-0">
                            <a href="/faq" class="modal-button cursor-pointer text-base">
                                <span class="w-6 h-6 mr-1"><Book /></span> FAQ
                            </a>
                        </li>
                        <li>
                            <a href="/contact" class="text-base">
                                <div class="w-6 h-6 mr-1"><Chat /></div> Contact
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/about" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" />
                                </svg>
                                About
                            </a>
                        </li>
                        {#if !isProduction()}
                            <li class="block md:hidden md:h-0 text-primary">
                                <span class="text-base">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 mr-1">
                                        <path fill-rule="evenodd" d="M11.097 1.515a.75.75 0 01.589.882L10.666 7.5h4.47l1.079-5.397a.75.75 0 111.47.294L16.665 7.5h3.585a.75.75 0 010 1.5h-3.885l-1.2 6h3.585a.75.75 0 010 1.5h-3.885l-1.08 5.397a.75.75 0 11-1.47-.294l1.02-5.103h-4.47l-1.08 5.397a.75.75 0 01-1.47-.294l1.02-5.103H3.75a.75.75 0 110-1.5h3.885l1.2-6H5.25a.75.75 0 010-1.5h3.885l1.08-5.397a.75.75 0 01.882-.588zM10.365 9l-1.2 6h4.47l1.2-6h-4.47z" clip-rule="evenodd" />
                                    </svg>
                                    <b>{getEnvironmentInfo()}</b>
                                </span>
                            </li>
                        {/if}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</nav>

<Modal bind:this={modal} content={null} />
