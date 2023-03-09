<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { browser } from "$app/environment";
    import { afterNavigate } from "$app/navigation";
    import { getValue } from 'btc2fiat';
    import { Pool } from "$lib/nostr/pool";
    import { decodeNpub } from "$lib/nostr/utils";
    import { ErrorHandler, getProfile, putProfile } from "$lib/services/api";
    import { token, user, BTC2USD, Info } from "$lib/stores";
    import { isProduction, getEnvironmentInfo, logout, requestLoginModal } from "$lib/utils";
    import Modal from "$lib/components/Modal.svelte";
    import TwitterUsername from "$lib/components/settings/TwitterUsername.svelte";
    import TwitterVerification from "$lib/components/settings/TwitterVerification.svelte";

    let modal: Modal | null;
    let modalVisible = false;

    let pool = new Pool();

    let prefersDark = true;

    let showMobileMenu = false;

    function toggleMobileMenu() {
        showMobileMenu = !showMobileMenu;
    }

    function hideMobileMenu() {
        showMobileMenu = false;
    }

    function toggleTheme() {
        let html = <HTMLHtmlElement>document.querySelector("html");
        let toggle = <HTMLInputElement>document.getElementById("theme-toggle");
        html.dataset.theme = toggle.checked ? "night" : "light";
    }

    function showModal(content: any, hasHide: boolean, onHide: (saved: boolean) => void = (_) => {}) {
        if (modal && modal.show && !modalVisible) {
            modal.content = content;
            modal.hasHide = hasHide;
            modal.onHide = (saved) => {
                modalVisible = false;
                onHide(saved);
            };
            modalVisible = true;
            modal.show();
        }
    }

    function fetchProfile(tokenValue) {
        getProfile(tokenValue, "me", (u) => { user.set(u); });
    }

    function saveProfile(nym, profileImageUrl) {
        putProfile(
            $token,
            { nym },
            (u) => {
                Info.set("Your nym has been imported from Nostr!");
                user.set(u);
                putProfile($token, { profileImageUrl },
                    (u) => {
                        Info.set(
                            "Your profile picture has been imported from Nostr!"
                        );
                        user.set(u);
                    }
                );
            },
            new ErrorHandler(false, (response) => {
                if (response.status === 400) {
                    response.json().then((data) => {
                        if (
                            data.field === "nym" &&
                            data.reason === "duplicated"
                        ) {
                            // append a random number and try again... best we can do, I guess,
                            // slightly nicer would be to append some Bip39 words...
                            setTimeout(() => {
                                saveProfile(
                                    nym +
                                        Math.trunc(
                                            Math.random() * 100
                                        ).toString(),
                                    profileImageUrl
                                );
                            }, 100);
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
                showModal(TwitterUsername, true, (saved) => {
                    if (saved) {
                        if ($user && !$user.twitterUsernameVerified) {
                            showModal(TwitterVerification, true);
                        }
                    } else {
                        // trying to hide the modal if you didn't set your Twitter username logges you out
                        logout();
                    }
                });
            }
        } else {
            if (u.nym === null || u.nym === "") {
                let gotProfile = false;
                pool.connectAndGetProfile(
                    decodeNpub(u.nostrPublicKey),
                    async (nostrProfile) => {
                        if (gotProfile) {
                            return;
                        }
                        gotProfile = true;

                        await pool.unsubscribeEverything();
                        await pool.disconnect();

                        let name = <string>nostrProfile.name;
                        name = name.replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
                        while (name.length < 3) {
                            name += "0"; // just pas with zeroes - not ideal, but they can always change it later
                        }

                        saveProfile(name, nostrProfile.picture);
                    }
                );
            }
        }
    });
    onDestroy(userUnsubscribe);

    afterNavigate(() => {
        hideMobileMenu();
    });
</script>

<nav class="backdrop-blur-lg border-b border-gray-400/70 z-50 fixed top-0 w-full">
    <div class="lg:w-2/3 py-2 px-4 mx-auto lg:flex lg:flex-row flex-col md:justify-between md:items-center">
        <div class="flex items-center justify-between">
            <a href="/" class="flex items-center mr-2">
                <div class="flex items-center space-x-2">
                    <img
                        src={"/images/logo.png"}
                        class="mr-3 h-9 rounded"
                        alt="Plebeian Technology"
                    />
                    <h1 class="text-xl font-bold hover:text-blue-400 duration-300 w-44">
                        Plebeian Market
                    </h1>
                </div>
            </a>
            <!-- Mobile menu button -->
            <div on:click={toggleMobileMenu} on:keydown={toggleMobileMenu} class="lg:hidden flex justify-end p-4">
                <button type="button" class="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                    </svg>
                </button>
            </div>
        </div>

        <!-- Mobile Menu open: "flex", Menu closed: "hidden" -->
        <div class:flex={showMobileMenu} class:hidden={!showMobileMenu} class="lg:flex lg:flex-row flex-col justify-center space-y-2 md:space-y-0 md:space-x-4">
            <!-- LINKS -->
            <div class="lg:flex items-center w-full">
                {#if !isProduction()}
                    <div class="lg:inline badge badge-primary ml-2 lg:my-0 hidden lg:block">
                        {getEnvironmentInfo()}
                    </div>
                {/if}

                <div class="lg:flex hidden">
                    <p>
                        <a href="/campaigns" class="btn btn-ghost normal-case">Campaigns</a>
                    </p>
                    <p>
                        <a href="/marketsquare" class="btn btn-ghost normal-case">Market Square</a>
                    </p>
                    <p>
                        <a href="/about" class="btn btn-ghost normal-case">About</a>
                    </p>
                    <p>
                        <a href="/faq" class="btn btn-ghost normal-case">FAQ</a>
                    </p>
                </div>
            </div>

            <!-- LIGHT MODE AND AVATAR -->
            <div class="lg:flex items-center justify-start space-x-4">
                <div class="flex justify-start lg:my-0 p-4 hidden lg:block">
                    <label class="swap swap-rotate" on:click={toggleTheme} on:keypress={toggleTheme}>
                        <input id="theme-toggle" type="checkbox" checked={prefersDark} />
                        <!-- sun icon -->
                        <svg class="swap-off fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" /></svg>
                        <!-- moon icon -->
                        <svg class="swap-on fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" /></svg>
                    </label>
                </div>

                <div class="lg:dropdown lg:dropdown-end">
                    {#if $token && $user}
                        <label role="button" for={null} tabindex="0" class="btn btn-ghost btn-circle avatar hidden lg:block"
                               class:verified={$user.twitterUsernameVerified} class:not-verified={!$user.twitterUsernameVerified}
                        >
                            <div class="w-10 rounded-full">
                                <img src={$user.profileImageUrl} alt="Avatar" />
                            </div>
                        </label>
                    {/if}

                    <ul role="menuitem" tabindex="0" class="p-2 shadow menu menu-compact dropdown-content bg-neutral text-white rounded-box w-60 z-40 float-right right-2">
                        {#if !isProduction()}
                            <li class="block md:hidden md:h-0 text-primary">
                                <a class="text-base">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
                                        <path fill-rule="evenodd" d="M11.097 1.515a.75.75 0 01.589.882L10.666 7.5h4.47l1.079-5.397a.75.75 0 111.47.294L16.665 7.5h3.585a.75.75 0 010 1.5h-3.885l-1.2 6h3.585a.75.75 0 010 1.5h-3.885l-1.08 5.397a.75.75 0 11-1.47-.294l1.02-5.103h-4.47l-1.08 5.397a.75.75 0 01-1.47-.294l1.02-5.103H3.75a.75.75 0 110-1.5h3.885l1.2-6H5.25a.75.75 0 010-1.5h3.885l1.08-5.397a.75.75 0 01.882-.588zM10.365 9l-1.2 6h4.47l1.2-6h-4.47z" clip-rule="evenodd" />
                                    </svg>
                                    <b>{getEnvironmentInfo()}</b>
                                </a>
                            </li>
                        {/if}
                        {#if !$token || !$user}
                            <li class="block md:hidden md:h-0 text-primary">
                                <a href="#" class="modal-button cursor-pointer text-base" on:click={() => {requestLoginModal(); hideMobileMenu()}} on:keypress={() => {requestLoginModal(); hideMobileMenu()}}>
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="text-primary" class="w-6 h-6 stroke-primary">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
                                    </svg>
                                    <b>Login</b>
                                </a>
                            </li>
                        {/if}

                        <li class="block md:hidden md:h-0">
                            <a href="/" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
                                Home
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/campaigns" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.25v8.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 109.375 7.5H12m0-2.625V7.5m0-2.625A2.625 2.625 0 1114.625 7.5H12m0 0V21m-8.625-9.75h18c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-18c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                                </svg>
                                Campaigns
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/marketsquare" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                                </svg>
                                Market Square
                            </a>
                        </li>
                        {#if $token && $user}
                            <li class="menu-title mt-3">
                                <span class="text-lg">Account</span>
                            </li>
                            {#if $token && $user && $user.twitterUsername !== null && !$user.twitterUsernameVerified}
                                <li class="text-red-600">
                                    <a on:click|preventDefault={() => showModal(TwitterVerification, true)} on:keypress={() => showModal(TwitterVerification, true)} class="modal-button text-base">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-6 h-6">
                                            <path fill="rgb(255,0,0)" d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
                                        </svg>
                                        Verify Twitter
                                    </a>
                                </li>
                            {/if}
                            <li>
                                <a rel="external" class="text-base" href="/stall/{$user.nym}">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
                                    </svg>
                                    My stall
                                </a>
                            </li>
                            {#if $user.isModerator}
                                <li>
                                    <a class="text-base" href="/account/campaigns">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                                        </svg>
                                        My campaigns
                                    </a>
                                </li>
                            {/if}
                            <li>
                                <a class="text-base" href="/account/purchases/">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
                                    </svg>
                                    My purchases</a>
                            </li>
                            <li>
                                <a class="text-base" href="/account/sales/">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                                    My sales
                                </a>
                            </li>
                            <li>
                                <a class="text-base" href="/account/settings">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M10.343 3.94c.09-.542.56-.94 1.11-.94h1.093c.55 0 1.02.398 1.11.94l.149.894c.07.424.384.764.78.93.398.164.855.142 1.205-.108l.737-.527a1.125 1.125 0 011.45.12l.773.774c.39.389.44 1.002.12 1.45l-.527.737c-.25.35-.272.806-.107 1.204.165.397.505.71.93.78l.893.15c.543.09.94.56.94 1.109v1.094c0 .55-.397 1.02-.94 1.11l-.893.149c-.425.07-.765.383-.93.78-.165.398-.143.854.107 1.204l.527.738c.32.447.269 1.06-.12 1.45l-.774.773a1.125 1.125 0 01-1.449.12l-.738-.527c-.35-.25-.806-.272-1.203-.107-.397.165-.71.505-.781.929l-.149.894c-.09.542-.56.94-1.11.94h-1.094c-.55 0-1.019-.398-1.11-.94l-.148-.894c-.071-.424-.384-.764-.781-.93-.398-.164-.854-.142-1.204.108l-.738.527c-.447.32-1.06.269-1.45-.12l-.773-.774a1.125 1.125 0 01-.12-1.45l.527-.737c.25-.35.273-.806.108-1.204-.165-.397-.505-.71-.93-.78l-.894-.15c-.542-.09-.94-.56-.94-1.109v-1.094c0-.55.398-1.02.94-1.11l.894-.149c.424-.07.765-.383.93-.78.165-.398.143-.854-.107-1.204l-.527-.738a1.125 1.125 0 01.12-1.45l.773-.773a1.125 1.125 0 011.45-.12l.737.527c.35.25.807.272 1.204.107.397-.165.71-.505.78-.929l.15-.894z" />
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                    Settings
                                </a>
                            </li>
                            <li>
                                <a href={null} on:click={() => {logout(); hideMobileMenu()}} class="modal-button cursor-pointer text-base">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                                    </svg>
                                    Logout
                                </a>
                            </li>

                            <li class="menu-title mt-3 text-base">
                                <span class="text-lg">Other information</span>
                            </li>
                        {/if}

                        <li class="block md:hidden md:h-0">
                            <a href="/about" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" />
                                </svg>
                                About
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/faq" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                                </svg>
                                FAQ
                            </a>
                        </li>
                        <li>
                            <a href="/contact" class="text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                                </svg>
                                Contact
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</nav>

<Modal bind:this={modal} content={null} />
