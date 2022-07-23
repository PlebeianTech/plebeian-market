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
        if ( themeToggle === 'Switch to Night Theme') {
            html.dataset.theme = 'night';
            themeToggle = 'Switch to Light Theme';
        } else {
            html.dataset.theme = 'light';
            themeToggle = 'Switch to Night Theme';
        }
    }

    function getProfileImage(user: User) {
        if (user.twitterProfileImageUrl) {
            return user.twitterProfileImageUrl
        }
        return "/images/default-profile.png";
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

<nav class="navbar bg-base-300 md:flex md:items-center justify-between">
    <div class="flex">
        <a href={getBaseUrl()} class="flex">
            <img src="/images/logo.jpg" class="w-10 h-10 rounded align-middle" alt="Plebeian Technology" />
            <span class="card-title text-2xl items-center text-primary ml-2">
                Plebeian Market
            </span>
        </a>
        {#if !isLocal() && !isStaging() } <!-- TODO: change this to || before pushing! -->
        <div class="badge badge-primary inline ml-2">{getEnvironmentInfo()}</div>
        {/if}
    </div>
    <div class="dropdown dropdown-end px-4 justify-end pt-2">
        {#if $token && $user}
        <label for={null} tabindex="0" class:verified={$user.twitterUsernameVerified} class:not-verified={!$user.twitterUsernameVerified} class="btn btn-ghost btn-circle avatar ring-2 ring-primary ring-offset-0">
            <div class="w-10 rounded-full">
                <img src={getProfileImage($user)} alt="Avatar" />
            </div>
        </label>
        {:else}
        <label for={null} tabindex="0" class="btn btn-ghost btn-circle avatar ring-2 ring-primary ring-offset-0">
            <div class="w-10 rounded-full">
                <img src="/images/default-profile.png" alt="Avatar" />
            </div>
        </label>
        {/if}
        <div>
            <ul tabindex="0" class="mt-3 p-3 shadow menu dropdown-content bg-base-100 rounded-box w-52">
                {#if $user && !$user.twitterUsernameVerified}
                    <li class="hover:bordered">
                        <label for="twitter-verification-modal" on:click|preventDefault={showTwitterVerification} class="modal-button cursor-pointer">
                            Verify Twitter
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="w-8 h-8">
                                <path fill="rgb(255,0,0)" d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
                            </svg>
                        </label>
                    </li>
                {/if}
                {#if $token && $user}
                <!-- user logged in -->
                <li class="hover:bordered"><a href={null} on:click|preventDefault={() => goto("/auctions")} class="cursor-pointer">My auctions</a></li>
                <li class="hover:bordered"><label for="profile-modal" on:click|preventDefault={showProfile} class="cursor-pointer">Profile</label></li>
                <li class="hover:bordered"><label for="profile-modal" on:click|preventDefault={showUserNotifications} class="cursor-pointer">Notifications</label></li>
                {/if}
                <!-- all users -->
                <li class="hover:bordered" on:click|preventDefault={toggleTheme}><span class="cursor-pointer">{themeToggle}</span></li>
                <li class="hover:bordered"><a href="https://t.me/PlebeianMarket" target="_blank">Telegram group</a></li>
                <!-- login / logout -->
                {#if $token && $user}
                <li class="hover:bordered"><a href={null} on:click|preventDefault={() => { token.set(null); localStorage.removeItem('token'); goto("/"); }} class="cursor-pointer">Logout</a></li>
                {:else}
                <li class="hover:bordered"><a href={null} on:click|preventDefault={() => { goto("/login"); }} class="cursor-pointer">Login</a></li>
                {/if}
            </ul>
        </div>
    </div>
</nav>

<Profile bind:this={profile} />
<UserNotifications bind:this={userNotifications} />
