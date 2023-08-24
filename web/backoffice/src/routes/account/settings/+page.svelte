<svelte:head>
    <title>Settings</title>
</svelte:head>

<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import { user } from "$lib/stores";
    import Email from "$lib/components/settings/Email.svelte";
    import Stall from "$lib/components/settings/Stall.svelte";
    import Nostr from "$lib/components/settings/Nostr.svelte";
    import Login from "$lib/components/settings/Login.svelte";
    import V4V from "$lib/components/settings/V4V.svelte";
    import Wallet from "$lib/components/settings/Wallet.svelte";
    import { goto } from '$app/navigation';

    let STALL_PAGE = "My Stall";
    let WALLET_PAGE = "Wallet";
    let EMAIL_PAGE = "Email";
    let NOSTR_PAGE = "Nostr";
    let LOGIN_PAGE = "Login";
    let V4V_PAGE = "Value 4 Value";
    let pages = [STALL_PAGE, LOGIN_PAGE, WALLET_PAGE, EMAIL_PAGE, NOSTR_PAGE, V4V_PAGE];
    let WALLET_PAGE_INDEX = pages.indexOf(WALLET_PAGE);
    let currentPage: string | null = null;

    let params = {};

    function onSaved() {
        if ($user && params['onsave'] === 'mystall') {
            goto("/admin");
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

        if (params['page'] === 'WALLET') {
            currentPage = pages[WALLET_PAGE_INDEX];
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
            <div>
                {#if currentPage === null || currentPage === STALL_PAGE}
                    <Stall onSave={onSaved} />
                {:else if currentPage === WALLET_PAGE}
                    <Wallet onSave={onSaved} />
                {:else if currentPage === EMAIL_PAGE}
                    <Email onSave={onSaved} />
                {:else if currentPage === NOSTR_PAGE}
                    <Nostr />
                {:else if currentPage === LOGIN_PAGE}
                    <Login />
                {:else if currentPage === V4V_PAGE}
                    <V4V />
                {/if}
            </div>
        </div>
    </div>
{/if}
