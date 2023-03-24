<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { toasts } from 'svelte-toasts';
    import "../app.css";
    import { browser } from '$app/environment';
    import { page } from '$app/stores';
    import { token, nostrUser, nostrPool, Info, Error, type Placement } from "$lib/stores";
    import Footer from "$lib/components/Footer.svelte";
    import LoginModal from "$lib/components/login/Modal.svelte";
    import Navbar from "$lib/components/Navbar.svelte";
    import ToastContainer from "$lib/components/ToastContainer.svelte";
    import {getPublicKey} from "nostr-tools";
    import {getProfileInfo, closePool} from "../lib/services/nostr";

    function getToastOnClickCB(data) {
        return () => {
            if (typeof data.onClick === 'function') {
                data.onClick();
                data.remove();
            }
        }
    }

	const infoUnsubscribe = Info.subscribe(value => {
        if (value) {
            let description: string;
            let duration: number;
            let url: string | null;
            let button: string | undefined;
            let placement: Placement;
            if (typeof value === 'string') {
                description = value;
                duration = 4000;
                url = null;
                button = undefined;
                placement = window.screen.availWidth >= 1024 ? 'top-center' : 'bottom-right';
            } else {
                description = value.message;
                duration = value.duration;
                url = value.url;
                button = value.button;
                placement = value.placement;
            }

            // HACK: here we use the "title" property of the toast to pass the *button* title to the toast container
            toasts.add({
                title: button,
                description,
                duration,
                placement,
                type: 'info',
                onClick: () => {
                    if (url) {
                        window.open(url, '_blank', window.screen.availWidth >= 1024 ? "width=500,height=500" : undefined);
                    }
                },
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
        if (browser) {
            // Legacy
            token.set(localStorage.getItem("token"));

            // Nostr
            let nosPrivKey = localStorage.getItem('nostrPrivateKey');

            if (nosPrivKey !== null) {
                let nosPubKey = getPublicKey(nosPrivKey);

                nostrUser.set({
                    privateKey: nosPrivKey,
                    publicKey: nosPubKey,
                });

                await getProfileInfo(
                    $nostrPool,
                    nosPubKey,
                    (profileInfo) => {
                        nostrUser.set({
                            privateKey: nosPrivKey,
                            publicKey: nosPubKey,
                            picture: profileInfo.picture || null,
                            displayName: profileInfo.name || null
                        });
                    }
                );
            }
        }
    });

    onDestroy(async () => {
        await closePool($nostrPool);
    });
</script>

<div class="h-screen pt-12 lg:pt-20 pb-20 mt-2">
    <Navbar />
    <div class="py-4" style="min-height: 83.33%">
        <slot />
    </div>
    {#if $page.url.pathname !== "/marketsquare"}
        <Footer />
    {/if}

    <ToastContainer let:data={data}>
        <div class:alert-error={data.type === 'error'} class:alert-info={data.type === 'info'} class="alert shadow-lg">
            <div>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <span class:text-2xl={data.placement === 'center-center'}>{data.description}</span>
            </div>
            {#if data.title}
                <div class="flex-none">
                    <button class="btn btn-sm" on:click={() => getToastOnClickCB(data)()}>{data.title}</button>
                </div>
            {/if}
          </div>
    </ToastContainer>
</div>

<LoginModal />
