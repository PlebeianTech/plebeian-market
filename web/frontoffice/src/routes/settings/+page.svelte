<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import Nostr from "$lib/components/settings/Nostr.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {NostrPublicKey} from "$lib/stores";
    import SetupHomepage from "$lib/components/settings/SetupHomepage.svelte";

    let NOSTR_PAGE = "Nostr";
    let SETUP_HOMEPAGE = "Setup homepage";
    let pages = [NOSTR_PAGE, SETUP_HOMEPAGE];
    let currentPage: string | null = NOSTR_PAGE;

    let params = {};

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

<svelte:head>
    <title>Settings</title>
</svelte:head>

<Titleh1>Settings</Titleh1>

<div class="lg:w-2/3 mx-auto grid lg:grid-cols-4 py-20 p-4">
    <div class="md:grow-0">
        <ul class="menu menu-compact mt-3 bg-base-100 md:w-52 p-2 rounded-box">
            {#each pages as page, i}
                <li><a class:active={page === currentPage} href={null} on:click={() => currentPage = page}>{page}</a></li>
            {/each}
        </ul>
    </div>
    <div class="col-span-3 w-full items-center justify-center">
        {#if currentPage === NOSTR_PAGE}
            <Nostr />
        {:else if currentPage === SETUP_HOMEPAGE}
            <SetupHomepage />
        {/if}
    </div>
</div>
