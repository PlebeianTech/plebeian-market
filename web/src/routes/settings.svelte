<svelte:head>
    <title>Settings</title>
</svelte:head>

<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import { user } from "$lib/stores";
    import Notifications from "$lib/components/settings/Notifications.svelte";
    import Stall from "$lib/components/settings/Stall.svelte";
    import TwitterUsername from "$lib/components/settings/TwitterUsername.svelte";
    import TwitterVerification from "$lib/components/settings/TwitterVerification.svelte";
    import V4V from "$lib/components/settings/V4V.svelte";
    import XPUB from "$lib/components/settings/XPUB.svelte";
    import { goto } from '$app/navigation';
    import { browser } from "$app/env";

    let STALL_PAGE = "My Stall";
    let WALLET_PAGE = "My wallet";
    let TWITTER_PAGE = "Twitter";
    let NOTIFICATIONS_PAGE = "Notifications";
    let V4V_PAGE = "Value 4 Value";
    let pages = [STALL_PAGE, WALLET_PAGE, TWITTER_PAGE, NOTIFICATIONS_PAGE, V4V_PAGE];
    let currentPage: string | null = null;

    function onStallSaved() {
        if ($user && $page.url.href.endsWith("#onsave=mystall")) {
            goto(`/stall/${$user.nym}`);
        }
    }

    onMount(async () => {
        if (browser) {
            localStorage.removeItem('initial-login-buyer'); // once the user opened settings, we don't want to pop up the verification anymore
        }
    });
</script>

{#if $user}
    <div class="md:flex py-5">
        <div class="md:grow-0">
            <ul class="menu menu-compact mt-3 bg-base-100 md:w-56 p-2 rounded-box">
                {#each pages as page, i}
                    <li><a class:active={(currentPage === null && i === 0) || (page === currentPage)} href={null} on:click={() => currentPage = page}>{page}</a></li>
                {/each}
            </ul>
        </div>
        <div class="md:grow mx-10">
            <div class="md:w-1/2">
                {#if currentPage === null || currentPage === STALL_PAGE}
                    <Stall onSave={onStallSaved} />
                {:else if currentPage === WALLET_PAGE}
                    <XPUB />
                {:else if currentPage === TWITTER_PAGE}
                    <TwitterUsername />
                    {#if !$user.twitterUsernameVerified}
                        <div class="mt-4">
                            <TwitterVerification />
                        </div>
                    {/if}
                {:else if currentPage === NOTIFICATIONS_PAGE}
                    <Notifications />
                {:else if currentPage === V4V_PAGE}
                    <V4V />
                {/if}
            </div>
        </div>
    </div>
{/if}