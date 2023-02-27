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

    let showMenu = false;

    function toggleNavbar() {
        showMenu = !showMenu;
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
        showMenu = false;
    });
</script>

<nav
    class="backdrop-blur-lg border-b border-gray-400/70 z-50 fixed top-0 w-full"
>
    <div
        class="lg:w-2/3 py-2 px-4 mx-auto lg:flex lg:flex-row flex-col md:justify-between md:items-center"
    >
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
                <a href="/" class="flex items-center mr-2">
                    <img
                        src={"/images/logo.png"}
                        class="mr-3 h-9 rounded"
                        alt="Plebeian Technology"
                    />
                    <h1
                        class="text-xl font-bold hover:text-blue-400 duration-300 w-44"
                    >
                        Plebeian Market
                    </h1>
                </a>
            </div>
            <!-- Mobile menu button -->
            <div
                on:click={toggleNavbar}
                on:keydown={() => {
                    toggleNavbar;
                }}
                class="lg:hidden flex justify-end"
            >
                <button
                    type="button"
                    class="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-400"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        class="w-6 h-6"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
                        />
                    </svg>
                </button>
            </div>
        </div>

        <!-- Mobile Menu open: "block", Menu closed: "hidden" -->
        <div class:flex={showMenu} class:hidden={!showMenu} class="lg:flex lg:flex-row flex-col justify-center mt-4 space-y-2 md:space-y-0 md:space-x-4 md:mt-0">
            <!-- LINKS -->
            <div class="lg:flex items-center w-full">
                {#if !isProduction()}
                    <div class="lg:inline badge badge-primary ml-2 lg:my-0 mt-4">
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
                <div class="flex justify-start lg:my-0 p-4">
                    <label class="swap swap-rotate" on:click={toggleTheme} on:keypress={toggleTheme}>
                        <input id="theme-toggle" type="checkbox" checked={prefersDark} />
                        <!-- sun icon -->
                        <svg class="swap-off fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" /></svg>
                        <!-- moon icon -->
                        <svg class="swap-on fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" /></svg>
                    </label>
                </div>
                {#if $token && $user}
                    <div class="lg:dropdown lg:dropdown-end">
                        <label role="button" for={null} tabindex="0" class:verified={$user.twitterUsernameVerified} class:not-verified={!$user.twitterUsernameVerified} class="btn btn-ghost btn-circle avatar">
                            <div class="w-10 rounded-full">
                                <img src={$user.profileImageUrl} alt="Avatar" />
                            </div>
                        </label>
                        <ul role="menuitem" tabindex="0" class="p-2 shadow menu menu-compact dropdown-content bg-neutral text-white rounded-box w-52 z-40">
                            {#if $user.twitterUsername !== null && !$user.twitterUsernameVerified}
                                <li>
                                    <label for="twitter-verification-modal" on:click|preventDefault={() => showModal(TwitterVerification, true)} on:keypress={() => showModal(TwitterVerification, true)} class="modal-button">
                                        Verify Twitter
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="w-8 h-8">
                                            <path fill="rgb(255,0,0)" d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
                                        </svg>
                                    </label>
                                </li>
                            {/if}
                            <li class="block md:hidden md:h-0">
                                <a href="/" class="modal-button cursor-pointer">Home</a>
                            </li>
                            <li class="block md:hidden md:h-0">
                                <a href="/campaigns" class="modal-button cursor-pointer">Campaigns</a>
                            </li>
                            <li class="block md:hidden md:h-0">
                                <a href="/marketsquare" class="modal-button cursor-pointer">Market Square</a>
                            </li>
                            <li class="block md:hidden md:h-0">
                                <a href="/about" class="modal-button cursor-pointer">About</a>
                            </li>
                            <li class="block md:hidden md:h-0">
                                <a href="/faq" class="modal-button cursor-pointer">FAQ</a>
                            </li>
                            <li>
                                <a rel="external" href="/stall/{$user.nym}">My stall</a>
                            </li>
                            {#if $user.isModerator}
                                <li>
                                    <a href="/account/campaigns">My campaigns</a>
                                </li>
                            {/if}
                            <li>
                                <a href="/account/purchases/">My purchases</a>
                            </li>
                            <li><a href="/account/sales/">My sales</a></li>
                            <li><a href="/account/settings">Settings</a></li>
                            <li>
                                <a href="https://t.me/PlebeianMarket" target="_blank" rel="noreferrer">Telegram group</a>
                            </li>
                            <li>
                                <a href={null} on:click={() => logout()} class="modal-button cursor-pointer">Logout</a>
                            </li>
                        </ul>
                    </div>
                {:else}
                    <div class="lg:dropdown lg:dropdown-end mb-96 lg:mb-2">
                        <button class="btn btn-primary" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
                    </div>
                {/if}
            </div>
        </div>
    </div>
</nav>

<Modal bind:this={modal} content={null} />
