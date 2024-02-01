<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import PageEditor from "$lib/components/settings/PageEditor.svelte";
    import NavbarSetup from "$lib/components/settings/NavbarSetup.svelte";
    import SiteConfig from "$lib/components/settings/SiteConfig.svelte";

    const pages = [
        {key: 'CMS', title: 'Page Editor'},
        {key: 'NAVBAR', title: 'Navigation Bar'},
        {key: 'SITECONF', title: 'Site config'},
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
    <title>CMS</title>
</svelte:head>

<Titleh1>CMS</Titleh1>

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
            <PageEditor />
        {:else if currentPage === 'NAVBAR'}
            <NavbarSetup />
        {:else if currentPage === 'SITECONF'}
            <SiteConfig />
        {/if}
    </div>
</div>
