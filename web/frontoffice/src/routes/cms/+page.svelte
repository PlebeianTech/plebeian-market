<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import Nostr from "$lib/components/settings/Nostr.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import SetupHomepage from "$lib/components/settings/SetupHomepage.svelte";
    import ExternalIdentities from "$lib/components/settings/ExternalIdentities.svelte";
    import NavbarSetup from "$lib/components/settings/NavbarSetup.svelte";

    const pages = [
        {key: 'CMS', title: 'CMS'},
        {key: 'NAVBAR', title: 'Navbar Config'},
    ];

    let currentPage = 'CMS';

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
            currentPage = params['page'];
        }
    });
</script>

<svelte:head>
    <title>Settings</title>
</svelte:head>

<Titleh1>Settings</Titleh1>

<div class="lg:grid lg:grid-cols-4 2xl:w-11/12 3xl:w-9/12 w-full p-0 md:p-4 pb-8 mx-auto">
    <div class="md:grow-0 pb-10">
        <ul class="md:w-52 mt-3 p-2 menu menu-compact bg-base-300 rounded-box">
            {#each pages as page}
                <li><a class:active={page.key === currentPage} href={null} on:click={() => currentPage = page.key}>{page.title}</a></li>
            {/each}
        </ul>
    </div>
    <div class="lg:col-span-3 w-full items-center justify-center">
        {#if currentPage === 'CMS'}
            <SetupHomepage />
        {:else if currentPage === 'NAVBAR'}
            <NavbarSetup />
        {/if}
    </div>
</div>
