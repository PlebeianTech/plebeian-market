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
    import Nostr from "$lib/components/settings/Nostr.svelte";
    import Lightning from "$lib/components/settings/Lightning.svelte";
    import V4V from "$lib/components/settings/V4V.svelte";
    import Wallet from "$lib/components/settings/Wallet.svelte";
    import { goto } from '$app/navigation';

    let STALL_PAGE = "My Stall";
    let WALLET_PAGE = "My wallet";
    let TWITTER_PAGE = "Twitter";
    let NOSTR_PAGE = "Nostr";
    let LIGHTNING_PAGE = "Lightning";
    let NOTIFICATIONS_PAGE = "Notifications";
    let V4V_PAGE = "Value 4 Value";
    let pages = [STALL_PAGE, WALLET_PAGE, NOSTR_PAGE, LIGHTNING_PAGE, NOTIFICATIONS_PAGE, V4V_PAGE];
    let currentPage: string | null = null;

    let params = {};

    function onSaved() {
        if ($user && params['onsave'] === 'mystall') {
            goto(`/stall/${$user.nym}`);
        }
    }

    onMount(async () => {
        let parts = $page.url.href.split("#");
        if (parts.length === 2) {
            for (let kv of parts[1].split("&")) {
                let [k, v] = kv.split("=");
                params[k] = v;
            }
        }

        if (params['page']) {
            currentPage = pages[parseInt(params['page'])];
        }
    });
</script>

{#if $user}
    <div class="lg:w-2/3 mx-auto grid lg:grid-cols-3 py-20 p-4">
        <div class="md:grow-0">
            <ul class="menu menu-compact mt-3 bg-base-100 md:w-56 p-2 rounded-box">
                {#each pages as page, i}
                    <li><a class:active={(currentPage === null && i === 0) || (page === currentPage)} href={null} on:click={() => currentPage = page}>{page}</a></li>
                {/each}
            </ul>
        </div>
        <div class="lg:w-2/3 col-span-2">
            <div class="">
                {#if currentPage === null || currentPage === STALL_PAGE}
                    <Stall onSave={onSaved} />
                {:else if currentPage === WALLET_PAGE}
                    <Wallet onSave={onSaved} />
                {:else if currentPage === TWITTER_PAGE}
                    <TwitterUsername />
                    {#if $user.twitterUsername !== null && !$user.twitterUsernameVerified}
                        <div class="mt-4">
                            <TwitterVerification />
                        </div>
                    {/if}
                {:else if currentPage === NOSTR_PAGE}
                    <Nostr />
                {:else if currentPage === LIGHTNING_PAGE}
                    <Lightning />
                {:else if currentPage === NOTIFICATIONS_PAGE}
                    <Notifications />
                {:else if currentPage === V4V_PAGE}
                    <V4V />
                {/if}
            </div>
        </div>
    </div>
{/if}
