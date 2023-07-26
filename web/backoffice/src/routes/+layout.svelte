<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { toasts, ToastContainer } from 'svelte-toasts';
    import "../app.css";
    import { browser } from '$app/environment';
    import { page } from '$app/stores';
    import { Info, Error, type Placement } from "$lib/stores";
    import { token } from "$sharedLib/stores";
    import Footer from "$sharedLib/components/Footer.svelte";
    import LoginModalLightning from "$lib/components/auth/Modal.svelte";
    import LoginModal from "$sharedLib/components/login/Modal.svelte";
    import Navbar from "$lib/components/Navbar.svelte";

	const infoUnsubscribe = Info.subscribe(value => {
        if (value) {
            let description: string;
            let duration: number;
            let placement: Placement;
            if (typeof value === 'string') {
                description = value;
                duration = 4000;
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
        if (browser) {
            token.set(localStorage.getItem("token"));
        }
    });
</script>

<div class="h-screen pt-12 lg:pt-20 pb-20 mt-2">
    <Navbar />

    <div class="mx-auto mb-6 min-h-[80%] { $page.url.pathname === '/admin' ? 'w-screen' : 'w-11/12 md:w-10/12' }">
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
          </div>
    </ToastContainer>
</div>

<LoginModal />
<LoginModalLightning />
