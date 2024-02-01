<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { toasts, ToastContainer } from 'svelte-toasts';
    import "../app.css";
    import { page } from '$app/stores';
    import {NostrPublicKey, isSuperAdmin, fileConfiguration, NostrGlobalConfig} from "$sharedLib/stores";
    import type { Placement} from "$sharedLib/stores";
    import {Info, Error} from "$sharedLib/stores";
    import LoginModal from "$sharedLib/components/login/Modal.svelte";
    import Navbar from "$sharedLib/components/Navbar.svelte";
    import Notifications from "$lib/components/Notifications.svelte";
    import Footer from "$sharedLib/components/Footer.svelte";
    import {closePool, getConfigurationKey, subscribeConfiguration} from "$sharedLib/services/nostr";
    import AlertInfo from "$sharedLib/components/icons/AlertInfo.svelte";
    import {refreshStalls, restoreShoppingCartProductsFromLocalStorage} from "$lib/shopping";
    import { browser } from "$app/environment";

    function subscribeGlobalConf() {
        let receivedAt = 0;

        const serializedGlobalConfig = localStorage.getItem("NostrGlobalConfig");
        if (serializedGlobalConfig) {
            $NostrGlobalConfig = JSON.parse(serializedGlobalConfig);
            receivedAt = parseInt(localStorage.getItem("NostrGlobalConfigReceivedAt") ?? '0');
        }

        subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('site_specific_config')],
            (setup, rcAt) => {
                if (rcAt > receivedAt) {
                    receivedAt = rcAt;

                    $NostrGlobalConfig = setup;
                    localStorage.setItem('NostrGlobalConfig', JSON.stringify(setup));
                    localStorage.setItem('NostrGlobalConfigReceivedAt', receivedAt.toString());
                }
            });
    }

    $: if ($fileConfiguration?.admin_pubkeys?.length > 0) {
        subscribeGlobalConf();
    }

    $: if ($NostrPublicKey && $fileConfiguration?.admin_pubkeys?.includes($NostrPublicKey)) {
        $isSuperAdmin = true;
    }

    const infoUnsubscribe = Info.subscribe(value => {
        if (value) {
            let description: string;
            let duration: number;
            let placement: Placement;
            if (typeof value === 'string') {
                description = value;
                duration = 5000;
                placement = window.screen.availWidth >= 1024 ? 'top-center' : 'bottom-right';
            } else {
                description = value.message;
                duration = value.duration;
                placement = value.placement;
            }

            toasts.add({
                description,
                duration,
                placement,
                type: 'info',
            });
            Info.set(null);
        }
    });

    const errorUnsubscribe = Error.subscribe(value => {
        if (value) {
            toasts.add({
                description: value,
                duration: 4000,
                placement: window.screen.availWidth >= 1024 ? 'top-center' : 'bottom-right',
                type: 'error'
            });
            Error.set(null);
        }
    });

    let favicon = null;

    onMount(() => {
        refreshStalls();
        restoreShoppingCartProductsFromLocalStorage();

        let content = $NostrGlobalConfig.content
        if (content && content.favicon) {
            favicon = content.favicon;
        }
    });

    onDestroy(async () => {
        errorUnsubscribe();
        infoUnsubscribe();
        if (browser) {
            await closePool();
        }

    });
</script>

<svelte:head>
    {#if favicon}
        <link rel="icon" type="image/svg" href={favicon} />
    {:else}
        <link rel="icon" type="image/png" sizes="32x32" href="/images/icons/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/images/icons/favicon-16x16.png">
        <link rel="apple-touch-icon" sizes="180x180" href="/images/icons/apple-touch-icon.png">
        <link rel="manifest" href="/images/icons/site.webmanifest">
        <link rel="mask-icon" href="/images/icons/safari-pinned-tab.svg" color="#5bbad5">
        <meta name="msapplication-TileColor" content="#da532c">
    {/if}
</svelte:head>

<div class="h-screen pt-12 lg:pt-20 pb-20 { $page.url.pathname === '/messages' ? '' : 'mt-2' }">
    <Navbar />

    <div class="mx-auto mb-6 min-h-[80%] { $page.url.pathname === '/messages' ? 'h-full' : '' } { $page.url.pathname === '/' ? 'w-screen' : 'w-11/12 lg:w-10/12' }">
        <Notifications />

        <slot />
    </div>

    {#if !['/marketsquare', '/messages'].includes($page.url.pathname)}
        <Footer />
    {/if}

    <ToastContainer let:data={data}>
        <div class:alert-error={data.type === 'error'} class:alert-info={data.type === 'info'} class="alert shadow-lg">
            <AlertInfo />
            <span class:text-2xl={data.placement === 'center-center'}>{data.description}</span>
        </div>
    </ToastContainer>
</div>

<LoginModal />
