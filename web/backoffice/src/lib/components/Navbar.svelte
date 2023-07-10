<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { browser } from "$app/environment";
    import { afterNavigate } from "$app/navigation";
    import { getValue } from 'btc2fiat';
    import { ErrorHandler, getProfile, putProfile } from "$lib/services/api";
    import { token, user, BTC2USD, Info, AuthRequired, AuthBehavior } from "$lib/stores";
    import type { User } from "$lib/types/user";
    import { isProduction, getEnvironmentInfo, logout, getBaseUrl } from "$lib/utils";
    import Modal from "$lib/components/Modal.svelte";
    import Cash from "$lib/components/icons/Cash.svelte";
    import Exit from "$lib/components/icons/Exit.svelte";
    import Hamburger from "$lib/components/icons/Hamburger.svelte";
    import Home from "$lib/components/icons/Home.svelte";
    import Key from "$lib/components/icons/Key.svelte";
    import Moon from "$lib/components/icons/Moon.svelte";
    import Settings from "$lib/components/icons/Settings.svelte";
    import Stall from "$lib/components/icons/Stall.svelte";
    import Sun from "$lib/components/icons/Sun.svelte";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    let modal: Modal | null;
    let modalVisible = false;

    let prefersDark = true;

    let showMobileMenu = false;

    function login() {
        AuthRequired.set({default: AuthBehavior.Login});
    }

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
        html.dataset.theme = toggle.checked ? "halloween" : "light";
    }

    function fetchProfile(tokenValue) {
        getProfile(tokenValue, "me", (u) => { user.set(u); });
    }

    function randomDigits() {
        return Math.trunc(Math.random() * 100).toString();
    }

    function saveNymWithRetry(nym, successCB: (u: User) => void) {
        putProfile($token,
            {nym},
            (u) => {
                user.set(u);
                successCB(u);
            },
            new ErrorHandler(false,
                (response) => {
                    if (response.status === 400) {
                        response.json().then(
                            (data) => {
                                if (data.field === "nym" && data.reason === "duplicated") {
                                    // append a random number and try again... best we can do, I guess,
                                    // slightly nicer would be to append some Bip39 words...
                                    setTimeout(() => saveNymWithRetry(nym + randomDigits(), successCB), 100);
                                }
                            });
                    }
                })
        );
    }

    async function fetchFiatRate() {
        BTC2USD.set(await getValue());
    }

    onMount(async () => {
        prefersDark =
            browser &&
            window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: dark)").matches;
        if ($token) {
            fetchProfile($token);
        }
        fetchFiatRate();
    });

    const tokenUnsubscribe = token.subscribe((t) => {
        if (t) {
            fetchProfile(t);
        } else {
            user.set(null);
        }
    });
    onDestroy(tokenUnsubscribe);
    const userUnsubscribe = user.subscribe((u) => {
        if (!u) {
            return;
        }

        if (u.nostrPublicKey === null) {
            if (u.nym === null || u.nym === "") {
                saveNymWithRetry("pleb" + randomDigits(),
                    (u) => {
                        Info.set(`Welcome, ${u.nym}!`);
                        putProfile($token, {profileImageUrl: getBaseUrl() + profilePicturePlaceHolder},
                            (u) => {
                                user.set(u);
                            });
                    });
            }
        }
    });
    onDestroy(userUnsubscribe);

    afterNavigate(() => {
        hideMobileMenu();
    });
</script>

<nav class="backdrop-blur-3xl border-b border-gray-400/70 z-50 fixed top-0 w-full">
    <div class="lg:w-2/3 py-2 px-4 mx-auto lg:flex lg:flex-row flex-col md:justify-between md:items-center">
        <div class="flex items-center justify-between">
            <a href="/admin" class="flex items-center mr-2">
                <div class="flex items-center space-x-2">
                    <img src={"/images/logo.png"} class="mr-3 h-9 rounded" alt="Plebeian Technology" />
                    <h1 class="text-xl font-bold hover:text-blue-400 duration-300">
                        Plebeian Market Stall Manager
                    </h1>
                </div>
            </a>
            <!-- Mobile menu button -->
            <div on:click={toggleMobileMenu} on:keydown={toggleMobileMenu} class="lg:hidden flex justify-end p-4">
                <button type="button" class="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-400 w-6 h-6"><Hamburger /></button>
            </div>
        </div>

        <!-- Mobile Menu open: "flex", Menu closed: "hidden" -->
        <div class:flex={showMobileMenu} class:hidden={!showMobileMenu} class="lg:flex lg:flex-row flex-col justify-center space-y-0 md:space-x-4">
            <!-- LINKS -->
            <div class="lg:flex items-center w-full">
                {#if !isProduction()}
                    <div class="lg:inline badge badge-primary ml-2 lg:my-0 hidden lg:block">
                        {getEnvironmentInfo()}
                    </div>
                {/if}

                <div class="lg:flex hidden">
                    <p>
                        <a href="/admin" class="btn btn-ghost normal-case">My stall</a>
                    </p>
                    <p>
                        <a href="/" class="btn btn-ghost normal-case">Buy items</a>
                    </p>
                    {#if !$token || !$user}
                        <p>
                            <a href={null} class="btn btn-ghost normal-case text-primary" on:click={() => login()} on:keypress={() => login()}><b>Login</b></a>
                        </p>
                    {/if}
                </div>
            </div>

            <div class="lg:flex items-center justify-start space-x-4">
                <div class="flex justify-start lg:my-0 p-4 hidden lg:block">
                    <label class="swap swap-rotate" on:click={toggleTheme} on:keypress={toggleTheme}>
                        <input id="theme-toggle" type="checkbox" checked={prefersDark} />
                        <div class="swap-off w-10 h-10"><Sun /></div>
                        <div class="swap-on w-10 h-10"><Moon /></div>
                    </label>
                </div>

                <div class="lg:dropdown lg:dropdown-end h-screen lg:h-fit" on:click={hideMobileMenu} on:keydown={hideMobileMenu}>
                    {#if $token && $user}
                        <label role="button" for={null} tabindex="0" class="btn btn-ghost btn-circle avatar hidden lg:block" class:verified={$user.twitterUsernameVerified} class:not-verified={!$user.twitterUsernameVerified}>
                            <img class="w-10 rounded-full" src={$user.profileImageUrl} alt="Avatar" />
                        </label>
                    {/if}

                    <ul role="menuitem" tabindex="0" class="p-2 shadow menu menu-compact dropdown-content bg-neutral text-white rounded-box w-60 z-40 float-right right-2">
                        {#if !$token || !$user}
                            <li class="block md:hidden md:h-0 text-primary">
                                <a href={null} class="modal-button cursor-pointer text-base" on:click={() => login()} on:keypress={() => { login(); hideMobileMenu(); }}>
                                    <span class="w-6 h-6"><Key /></span> <b>Login</b>
                                </a>
                            </li>
                        {/if}

                        <li class="block md:hidden md:h-0">
                            <a href="/admin" class="modal-button cursor-pointer text-base">
                                <span class="w-6 h-6"><Home /></span> My stall
                            </a>
                        </li>
                        {#if $token && $user}
                            <li>
                                <a class="text-base" href="/admin/account/orders/">
                                    <span class="w-6 h-6"><Cash /></span> Orders
                                </a>
                            </li>
                            <li>
                                <a class="text-base" href="/admin/account/settings">
                                    <span class="w-6 h-6"><Settings /></span> Settings
                                </a>
                            </li>
                            <li>
                                <a href={null} on:click={() => { logout(); hideMobileMenu(); }} class="modal-button cursor-pointer text-base">
                                    <span class="w-6 h-6"><Exit /></span> Logout
                                </a>
                            </li>
                        {/if}
                        <li class="block md:hidden md:h-0">
                            <a href="/" class="modal-button cursor-pointer text-base">
                                <span class="w-6 h-6"><Stall /></span> Marketplace
                            </a>
                        </li>
                        {#if !isProduction()}
                            <li class="block md:hidden md:h-0">
                                <span class="badge badge-primary">
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
