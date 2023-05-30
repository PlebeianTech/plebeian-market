<script lang="ts">
    import { onMount } from 'svelte';
    import { afterNavigate } from "$app/navigation";
    import { getValue } from 'btc2fiat';
    import { BTC2USD, NostrPublicKey } from "$lib/stores";
    import { isProduction, getEnvironmentInfo, logout } from "$lib/utils";
    import Modal from "$lib/components/Modal.svelte";
    import {ShoppingCart} from "$lib/stores.js";
    import CompactShoppingCart from "$lib/components/stores/ShoppingCart.svelte";
    import ShoppingCartIcon from "$sharedLib/components/icons/ShoppingCart.svelte";
    import Settings from "$sharedLib/components/icons/Settings.svelte";
    import PrivateMessages from "$lib/components/nostr/PrivateMessages.svelte";
    import ProfilePicture from "$lib/components/nostr/ProfilePicture.svelte";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import World from "$sharedLib/components/icons/World.svelte";
    import { requestLoginModal } from "$lib/utils";

    let modal: Modal | null;

    let prefersDark = true;

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
        let toggle = <HTMLInputElement>document.getElementById("theme-toggle");

        if (toggle.checked) {
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
        let html = <HTMLHtmlElement>document.querySelector("html");

        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            html.dataset.theme = "dark";
            prefersDark = true;
        } else {
            html.dataset.theme = "light";
            prefersDark = false;
        }

        // await fetchFiatRate();
    });

    afterNavigate(() => {
        hideMobileMenu();
    });
</script>

<nav class="fixed top-0 w-full backdrop-blur-3xl border-b border-gray-400/70 z-50">
    <div class="lg:w-3/4 py-2 px-4 mx-auto lg:flex lg:flex-row flex-col md:justify-between md:items-center">
        <div class="flex items-center justify-between">
            <a href="/" class="flex items-center mr-2">
                <div class="flex items-center space-x-2">
                    <img src={"/images/logo.png"} class="mr-3 h-9 rounded" alt="Plebeian Technology" />
                    <h1 class="w-64 text-xl font-bold hover:text-blue-400 duration-300">
                        Plebeian Market
                    </h1>
                </div>
            </a>

            <!-- LINKS -->
            <div class="lg:flex items-right w-full">
                {#if !isProduction()}
                    <div class="lg:inline badge badge-primary ml-2 lg:my-0 hidden">
                        {getEnvironmentInfo()}
                    </div>
                {/if}

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
                    <p>
                        <a href="/admin" class="btn btn-ghost normal-case">Sell items</a>
                    </p>
                    <p>
                        {#if !$NostrPublicKey}
                            <a href={null} class="btn btn-ghost normal-case text-primary" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}><b>Login</b></a>
                        {:else}
                            <a href={null} class="btn btn-ghost normal-case" on:click={() => logout()} on:keypress={() => logout()}><b>Logout</b></a>
                        {/if}
                    </p>
                </div>
            </div>

            <!-- Mobile menu button -->
            <div on:click={toggleMobileMenu} on:keydown={toggleMobileMenu} class="lg:hidden flex justify-end p-4">
                <button type="button" class="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                    </svg>
                </button>
            </div>
        </div>

        <div class:flex={showMobileMenu} class:hidden={!showMobileMenu} class="lg:flex lg:flex-row flex-col justify-center space-y-0 md:space-x-4">
            <div class="lg:flex items-center justify-start space-x-4">
                <div class="float-right">
                    <label class="swap swap-rotate mr-2" on:click={toggleTheme} on:keypress={toggleTheme}>
                        <input id="theme-toggle" type="checkbox" checked={prefersDark} />
                        <span class="w-9 h-9">
                            <!-- sun icon -->
                            <svg class="swap-off fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" /></svg>
                            <!-- moon icon -->
                            <svg class="swap-on fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" /></svg>
                        </span>
                    </label>

                    <div class="dropdown dropdown-end mr-2">
                        <label tabindex="0" class="btn btn-ghost btn-circle">
                            <div class="indicator">
                                <ShoppingCartIcon />
                                <span class="badge badge-sm badge-info indicator-item">{$ShoppingCart.summary.totalQuantity}</span>
                            </div>
                        </label>
                        <div tabindex="0" class="mt-3 card card-compact card-bordered border-black dark:border-white dropdown-content w-fit bg-base-100 shadow-xl">
                            <div class="card-body">
                                <CompactShoppingCart compact=true></CompactShoppingCart>
                            </div>
                        </div>
                    </div>

                    <div class="btn btn-ghost btn-circle mr-3">
                        <PrivateMessages />
                    </div>
                </div>

                <div class="lg:dropdown lg:dropdown-end h-screen lg:h-fit clear-both" on:click={hideMobileMenu} on:keydown={hideMobileMenu}>
                    <ProfilePicture />

                    <ul role="menuitem" tabindex="0" class="p-2 shadow menu menu-compact dropdown-content bg-neutral text-white rounded-box w-60 z-40 float-right right-2">

                        {#if !$NostrPublicKey}
                            <li class="block md:hidden md:h-0 text-primary">
                                <a href={null} class="modal-button cursor-pointer text-base" on:click={() => {requestLoginModal(); hideMobileMenu()}} on:keypress={() => {requestLoginModal(); hideMobileMenu()}}>
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="text-primary" class="w-6 h-6 mr-1 stroke-primary">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
                                    </svg>
                                    <b>Login</b>
                                </a>
                            </li>
                        {/if}

                        <li class="block md:hidden md:h-0">
                            <a href="/" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
                                Home
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/stalls" class="modal-button cursor-pointer text-base">
                                <div class="w-6 h-6 mr-1">
                                    <Store />
                                </div>
                                Stall Browser
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/universe" class="modal-button cursor-pointer text-base">
                                <div class="w-6 h-6 mr-1">
                                    <World />
                                </div>
                                ¡Universe!
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/marketsquare" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                                </svg>
                                Market Square
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/skills" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z" />
                                </svg>
                                Skills Market
                            </a>
                        </li>
                        {#if $NostrPublicKey}
                            <li class="menu-title mt-2">
                                <span class="text-lg">Account</span>
                            </li>
                            <li>
                                <a class="text-base" href="/orders">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
                                    </svg>
                                    Orders</a>
                            </li>
                            <li>
                                <a class="text-base" href="/settings">
                                    <span class="w-6 h-6"><Settings /></span> Settings
                                </a>
                            </li>
                            <li>
                                <a href={null} on:click={() => {logout(); hideMobileMenu()}} class="modal-button cursor-pointer text-base">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                                    </svg>
                                    Logout
                                </a>
                            </li>

                            <li class="menu-title mt-2 text-base">
                                <span class="text-lg">Other information</span>
                            </li>
                        {/if}

                        <li class="block md:hidden md:h-0">
                            <a href="/faq" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                                </svg>
                                FAQ
                            </a>
                        </li>
                        <li>
                            <a href="/contact" class="text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-1">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                                </svg>
                                Contact
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
