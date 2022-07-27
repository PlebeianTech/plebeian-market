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
    let menuDisplay = "hidden";
    let prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
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

    function toggleTheme() {
        let html = <HTMLHtmlElement>document.querySelector('html');
        let toggle = <HTMLInputElement>document.getElementById('theme-toggle');
        html.dataset.theme = toggle.checked ? 'night' : 'light';
    }

    function toggleMenu() {
        menuDisplay = menuDisplay === "hidden" ? "block" : "hidden";
    }

    function getProfileImage(user: User) {
        if (user.twitterProfileImageUrl) {
            return user.twitterProfileImageUrl
        }
    }

    onMount(async () => {
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
        {#if isLocal() || isStaging() }
            <div class="inline badge badge-primary ml-2">{getEnvironmentInfo()}</div>
        {/if}
    </a>
    <div class="hidden md:block">
        <a class="rounded btn btn-ghost normal-case text-xl ml-4" href={getBaseUrl()} on:click={closeMenu}>
            Home
        </a>
        <a class="rounded btn btn-ghost normal-case text-xl" href="{getBaseUrl()}about" on:click={closeMenu}>
            About
        </a>
        <a class="rounded btn btn-ghost normal-case text-xl" href="{getBaseUrl()}faq" on:click={closeMenu}>
            FAQ
        </a>
    </div>
    <label class="rounded btn btn-ghost swap swap-rotate" on:click={toggleTheme} on:click={closeMenu}>
        <input id="theme-toggle" type="checkbox" checked={prefersDark} />
        <!-- sun icon -->
        <svg class="swap-off fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"/></svg>
        <!-- moon icon -->
        <svg class="swap-on fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z"/></svg>
    </label>
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
            <a class="md:hidden px-3 py-2 rounded btn btn-ghost" href="{getBaseUrl()}about">
                About
            </a>
            <a class="md:hidden px-3 py-2 rounded btn btn-ghost" href="{getBaseUrl()}faq">
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
