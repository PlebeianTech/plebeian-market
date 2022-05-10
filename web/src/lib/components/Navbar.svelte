<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { fetchAPI } from "../services/api";
    import { token, user } from "../stores";
    import { fromJson } from "../types/user";
    import Profile from "./Profile.svelte";

    let profile;

    function fetchProfile(tokenValue) {
        fetchAPI("/users/me", 'GET', tokenValue, null,
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        user.set(fromJson(data.user));
                        profile.showIfIncomplete();
                    });
                }
            });
    }

    onMount(async () => {
        if ($token) {
            fetchProfile($token);
        }
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
    <div class="flex-1">
        <a href={null} on:click|preventDefault={() => goto("/")} class="btn btn-ghost normal-case text-xl">Home</a>
        <a href={null} on:click|preventDefault={() => goto("/about")} class="btn btn-ghost normal-case text-xl">About</a>
    </div>
    <div class="flex-none gap-2">
        {#if $token && $user}
            <div class="dropdown dropdown-end">
                <label for={null} tabindex="0" class="btn btn-ghost btn-circle avatar">
                    <div class="w-10 rounded-full">
                        <img src={$user.twitterProfileImageUrl} alt="Avatar" />
                    </div>
                </label>
                <ul tabindex="0" class="mt-3 p-2 shadow menu menu-compact dropdown-content bg-base-100 rounded-box w-52">
                    <li><a href={null} on:click|preventDefault={() => goto("/auctions")}>My auctions</a></li>
                    <li><label for="profile-modal" on:click|preventDefault={profile.show} class="modal-button">Profile</label></li>
                    <li><a href={null} on:click|preventDefault={() => { token.set(null); localStorage.removeItem('token'); goto("/"); }}>Logout</a></li>
                </ul>
            </div>
        {/if}
    </div>
</div>

<Profile bind:this={profile} />