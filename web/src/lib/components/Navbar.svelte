<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { getValue } from 'btc2fiat';
    import { getProfile } from "../services/api";
    import { token, user, BTC2USD } from "../stores";
    import { isLocal, isStaging, getBaseUrl } from "../utils";
    import Profile from "./Profile.svelte";
    import UserNotifications from "./UserNotifications.svelte";

    let profile : Profile | null;
    let userNotifications : UserNotifications | null;

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

    function toggleTheme() {
        let html = <HTMLHtmlElement>document.querySelector('html');
        let toggle = <HTMLInputElement>document.getElementById('theme-toggle');
        html.dataset.theme = toggle.checked ? 'night' : 'light';
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

<div class="navbar bg-base-300">
    <div>
        <a href={getBaseUrl()}>
            <img src="/images/logo.jpg" class="mr-3 h-6 sm:h-9 rounded" alt="Plebeian Technology" />
        </a>
    </div>
    {#if isLocal()}
        <div class="badge badge-primary">dev (local API)</div>
    {:else if isStaging()}
        <div class="badge badge-primary">staging (staging API)</div>
    {/if}
    <div class="flex-1 invisible md:visible">
        <a href={null} on:click|preventDefault={() => goto("/")} class="btn btn-ghost normal-case text-xl invisible md:visible">Home</a>
        <a href={null} on:click|preventDefault={() => goto("/about")} class="btn btn-ghost normal-case text-xl invisible md:visible">About</a>
        <a href={null} on:click|preventDefault={() => goto("/faq")} class="btn btn-ghost normal-case text-xl invisible md:visible">FAQ</a>
    </div>
    <div class="flex-none gap-2">
        <label class="swap swap-rotate" on:click={toggleTheme}>
            <input id="theme-toggle" type="checkbox" checked={prefersDark} />
            <!-- sun icon -->
            <svg class="swap-off fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"/></svg>
            <!-- moon icon -->
            <svg class="swap-on fill-current w-10 h-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z"/></svg>
        </label>
        {#if $token && $user}
            <div class="dropdown dropdown-end">
                <label for={null} tabindex="0" class:verified={$user.twitterUsernameVerified} class:not-verified={!$user.twitterUsernameVerified} class="btn btn-ghost btn-circle avatar">
                    <div class="w-10 rounded-full">
                        <img src={$user.twitterProfileImageUrl} alt="Avatar" />
                    </div>
                </label>
                <ul tabindex="0" class="mt-3 p-2 shadow menu menu-compact dropdown-content bg-base-100 rounded-box w-52">
                    {#if !$user.twitterUsernameVerified}
                        <li>
                            <label for="twitter-verification-modal" on:click|preventDefault={showTwitterVerification} class="modal-button">
                                Verify Twitter
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="w-8 h-8">
                                    <path fill="rgb(255,0,0)" d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                                </svg>
                            </label>
                        </li>
                    {/if}
                    <li class="visible md:invisible md:h-0"><a href={null} on:click|preventDefault={() => goto("/")} class="modal-button cursor-pointer">Home</a></li>
                    <li class="visible md:invisible md:h-0"><a href={null} on:click|preventDefault={() => goto("/about")} class="modal-button cursor-pointer">About</a></li>
                    <li class="visible md:invisible md:h-0"><a href={null} on:click|preventDefault={() => goto("/faq")} class="modal-button cursor-pointer">FAQ</a></li>
                    <li><a href={null} on:click|preventDefault={() => goto("/auctions")}>My auctions</a></li>
                    <li><a href="{getBaseUrl()}stores/{$user.twitterUsername}">My store</a></li>
                    {#if $user.isModerator}
                        <li><a href={null} on:click|preventDefault={() => goto("/campaigns")}>My campaigns</a></li>
                    {/if}
                    <li><label for="profile-modal" on:click|preventDefault={showProfile} class="modal-button cursor-pointer">Profile</label></li>
                    <li><label for="profile-modal" on:click|preventDefault={showUserNotifications} class="modal-button cursor-pointer">Notifications</label></li>
                    <li><a href="https://t.me/PlebeianMarket" target="_blank">Telegram group</a></li>
                    <li><a href={null} on:click|preventDefault={() => { token.set(null); localStorage.removeItem('token'); goto("/"); }} class="modal-button cursor-pointer">Logout</a></li>
                </ul>
            </div>
        {/if}
    </div>
</div>

<Profile bind:this={profile} />
<UserNotifications bind:this={userNotifications} />
