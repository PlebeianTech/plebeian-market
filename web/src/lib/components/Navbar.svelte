<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { getValue } from 'btc2fiat';
    import { getProfile } from "../services/api";
    import { token, user, BTC2USD } from "../stores";
    import { getBaseUrl, getEnvironmentInfo, isLocal, isStaging } from "../utils";
    import type { User } from "../types/user";
    import Profile from "./Profile.svelte";
    import UserNotifications from "./UserNotifications.svelte";

    let profile : Profile | null;
    let userNotifications : UserNotifications | null;
    let themeToggle = "Switch to Light Theme";
    let menuDisplay = "hidden";
    function fetchProfile(tokenValue) {
        getProfile(tokenValue,
            u => {
                user.set(u);
                if (profile) {
                    profile.showIfIncomplete();
                }
            });
    }

    async function fetchFiatRate() {
        BTC2USD.set(await getValue());
    }

    function showProfile() {
        if (profile) {
            localStorage.removeItem('initial-login-seller'); // to allow twitter verification to be shown automatically if username changed
            profile.show();
        }
    }

    function showTwitterVerification() {
        if (profile) {
            profile.showTwitterVerification($user!.twitterUsernameVerificationTweet);
        }
    }

    function showUserNotifications() {
        if (userNotifications) {
            userNotifications.show();
        }
    }

    function closeMenu() {
        menuDisplay = "hidden";
    }

    function openMenu() {
        menuDisplay = "block";
    }

    function toggleMenu() {
        if ( menuDisplay === "block") {
            closeMenu();
        } else if ( menuDisplay === "hidden") {
            openMenu();
        }
    }

    function toggleTheme() {
        let html = <HTMLHtmlElement>document.querySelector('html');
        console.log(html.dataset.theme );
        if ( html.dataset.theme === 'night') {
            setLightTheme(html);
        } else {
            setDarkTheme(html);
        }
    }

    function setDarkTheme(html: HTMLHtmlElement) {
        html.dataset.theme = 'night';
        themeToggle = 'Switch to Light Theme';
    }

    function setLightTheme(html: HTMLHtmlElement) {
        html.dataset.theme = 'light';
        themeToggle = 'Switch to Night Theme';
    }

    function getProfileImage(user: User) {
        if (user.twitterProfileImageUrl) {
            return user.twitterProfileImageUrl
        }
    }

    onMount(async () => {
        let html = <HTMLHtmlElement>document.querySelector('html');
        setDarkTheme(html);
        if ($token) {
            fetchProfile($token);
        }
        fetchFiatRate();
    });

    const unsubscribe = token.subscribe(value => {
        if (profile === undefined) {
            return;
        }
        if (value) {
            fetchProfile(value);
        } else {
            user.set(null);
        }
    });
    onDestroy(unsubscribe);
</script>

<nav class="navbar flex items-center bg-base-300 flex-wrap">
    <a href={getBaseUrl()} class="flex" on:click={closeMenu}>
        <img src="/images/logo.jpg" class="w-10 h-10 rounded align-middle" alt="Plebeian Technology" />
        <span class="md:hidden inline-block card-title text-2xl items-center text-primary ml-2">
            Plebeian Market
        </span>
        {#if isLocal() || isStaging() }
            <!-- hiddin on small devices -->
            <div class="hidden md:inline badge badge-primary ml-2">{getEnvironmentInfo()}</div>
        {/if}
    </a>
    <div class="hidden md:block">
        <a class="rounded btn btn-ghost normal-case text-xl" href={null} on:click|preventDefault={() => goto("/")}>
            Home
        </a>
        <a class="rounded btn btn-ghost normal-case text-xl" href={null} on:click|preventDefault={() => goto("/about")}>
            About
        </a>
        <a class="rounded btn btn-ghost normal-case text-xl" href={null} on:click|preventDefault={() => goto("/faq")}>
            FAQ
        </a>
    </div>
    <div class="ml-auto pb-2 pt-1 pr-1" on:click={toggleMenu}>
        {#if $token && $user && $user.twitterProfileImageUrl}
        <label class="btn btn-ghost btn-circle avatar ring-2 ring-primary ring-offset-0" for={null} class:verified={$user.twitterUsernameVerified} class:not-verified={!$user.twitterUsernameVerified}>
            <div class="w-10 rounded-full">
                <img class="overflow-hidden" src={getProfileImage($user)} alt="Avatar" />
            </div>
        </label>
        {:else}
        <label class="btn btn-ghost btn-circle avatar ring-2 ring-primary ring-offset-0" for={null} >
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="currentColor" class="bi bi-list" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"/>
            </svg>
        </label>
        {/if}
    </div>
    <div class="{menuDisplay} w-full">
        <ul class="flex flex flex-col" on:click={closeMenu}>
            <a class="md:hidden px-3 py-2 rounded btn btn-ghost" href={null} on:click|preventDefault={() => goto("/about")}>
                About
            </a>
            <a class="md:hidden px-3 py-2 rounded btn btn-ghost" href={null} on:click|preventDefault={() => goto("/faq")}>
                FAQ
            </a>
            {#if $user && !$user.twitterUsernameVerified}
                <li class="pr-3 py-2 rounded btn btn-ghost" on:click|preventDefault={showTwitterVerification}>
                    <label class="flex flex-row cursor-pointer pt-2" for="twitter-verification-modal" >
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="w-8 h-8 ml-2">
                            <path fill="rgb(255,0,0)" d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                        </svg>
                        Verify Twitter
                    </label>
                </li>
            {/if}
            {#if $token && $user}
            <!-- user logged in -->
            <a class="px-3 py-2 rounded btn btn-ghost cursor-pointer" href={null} on:click|preventDefault={() => goto("/auctions")}>
                My auctions
            </a>
            {#if $user.isModerator}
            <a class="px-3 py-2 rounded btn btn-ghost cursor-pointer" href={null} on:click|preventDefault={() => goto("/campaigns")}>My campaigns</a>
            {/if}
            <li class="px-3 py-2 rounded btn btn-ghost cursor-pointer" on:click|preventDefault={showProfile}>
                <label class="cursor-pointer" for="profile-modal">Profile</label>
            </li>
            <li class="px-3 py-2 rounded btn btn-ghost cursor-pointer" on:click|preventDefault={showUserNotifications}>
                <label class="cursor-pointer" for="profile-modal">Notifications</label>
            </li>
            {/if}
            <!-- all users -->
            <li class="px-3 py-2 rounded btn btn-ghost cursor-pointer" on:click|preventDefault={toggleTheme}>
                <span>{themeToggle}</span>
            </li>
            <a class="px-3 py-2 rounded btn btn-ghost" href="https://t.me/PlebeianMarket"  target="_blank">
                Telegram
            </a>
            <a class="px-3 py-2 rounded btn btn-ghost" href="https://plebeianmarket.substack.com/"  target="_blank">
                Substack
            </a>
            <!-- login / logout -->
            {#if $token && $user}
            <a class="px-3 py-2 rounded btn btn-ghost cursor-pointer" href={null} on:click|preventDefault={() => { token.set(null); localStorage.removeItem('token'); goto("/");}}>
                Logout
            </a>
            {:else}
            <a class="px-3 py-2 rounded btn btn-ghost cursor-pointer" href={null} on:click|preventDefault={() => goto("/login")}>
                Login
            </a>
            {/if}
        </ul>
    </div>
</nav>

<Profile bind:this={profile} />
<UserNotifications bind:this={userNotifications} />
