<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { toasts, ToastContainer } from 'svelte-toasts';
    import "../app.css";
    import { page } from '$app/stores';
    import { NostrGlobalConfig } from "$lib/stores";
    import type { Placement} from "$sharedLib/stores";
    import {
        Info,
        Error,
    } from "$sharedLib/stores";

    import LoginModal from "$sharedLib/components/login/Modal.svelte";
    import Navbar from "$sharedLib/components/Navbar.svelte";
    import Notifications from "$lib/components/Notifications.svelte";
    import Footer from "$sharedLib/components/Footer.svelte";
    import {closePool, subscribeConfiguration} from "$sharedLib/services/nostr";
    import {getConfigurationFromFile} from "$sharedLib/utils";
    import AlertInfo from "$sharedLib/components/icons/AlertInfo.svelte";
    import {refreshStalls, restoreShoppingCartProductsFromLocalStorage} from "$lib/shopping";

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
	onDestroy(infoUnsubscribe);

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
	onDestroy(errorUnsubscribe);

    onMount(async () => {
        refreshStalls();

        let receivedAt = 0;

        let config = await getConfigurationFromFile();

        if (config && config.admin_pubkey.length === 64) {
            subscribeConfiguration(config.admin_pubkey,
                (setup, rcAt) => {
                    if (rcAt > receivedAt) {
                        receivedAt = rcAt;
                        $NostrGlobalConfig = setup;
                    }
                })
        }

        restoreShoppingCartProductsFromLocalStorage();
    });

    onDestroy(async () => {
        await closePool();
    });
</script>

<div class="h-screen pt-12 lg:pt-20 pb-20 { $page.url.pathname === '/messages' ? '' : 'mt-2' }">
    <Navbar />

    <div class="mx-auto mb-6 min-h-[80%] { $page.url.pathname === '/messages' ? 'h-full' : '' } { $page.url.pathname === '/' ? 'w-screen' : 'w-11/12 md:w-10/12' }">
        <Notifications />

        <slot />
    </div>

    {#if !['/marketsquare', '/messages'].includes($page.url.pathname)}
        <Footer />
    {/if}

    <ToastContainer let:data={data}>
        <div class:alert-error={data.type === 'error'} class:alert-info={data.type === 'info'} class="alert shadow-lg">
            <div>
                <AlertInfo />
                <span class:text-2xl={data.placement === 'center-center'}>{data.description}</span>
            </div>
        </div>
    </ToastContainer>
</div>

<LoginModal />
