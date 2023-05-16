<script lang="ts">
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { ErrorHandler, lnurlAuth } from "$lib/services/api";
    import { token, user, Info, AuthBehavior } from "$lib/stores";
    import Loading from "$lib/components/Loading.svelte";
    import QR from "$lib/components/QR.svelte";
    import { isDevelopment } from "$lib/utils";
    import type { User } from "$lib/types/user";
    import ErrorBox from "$lib/components/notifications/ErrorBox.svelte";
    import Wallets from '$lib/components/notifications/Wallets.svelte';

    const dispatch = createEventDispatcher();

    export let behavior: AuthBehavior;
    export let onLogin: (user: User | null) => void = (_) => {};

    let lnurl;
    let qr;
    let k1: string | null = null;

    let checkLoginTimeout: ReturnType<typeof setTimeout> | null = null;

    function stopCheckingLogin() {
        if (checkLoginTimeout !== null) {
            clearTimeout(checkLoginTimeout);
        }
        k1 = null;  // k1 cannot be used again if logout is done
    }

    function checkLogin() {
        lnurlAuth(behavior, k1,
            (response) => {
                k1 = response.k1;
                lnurl = response.lnurl;
                qr = response.qr;
                checkLoginTimeout = setTimeout(checkLogin, 1000);
            },
            () => {
                checkLoginTimeout = setTimeout(checkLogin, 1000);
            },
            async (response) => {
                token.set(response.token);
                localStorage.setItem('token', response.token);
                dispatch('login', {})

                if (behavior !== AuthBehavior.Signup) {
                    Info.set("¡Hello, you're so early!");
                }

                while ($user === null) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }

                onLogin(response.user);
            },
            () => {
                dispatch('loginTokenExpiredEvent', {})
            }, new ErrorHandler(true,
                (response) => {
                    if (response.status === 400 || response.status === 409) {
                        k1 = null;
                        checkLoginTimeout = setTimeout(checkLogin, 1000);
                    }
                }));
    }

    onMount(async () => {
        if ($token) {
            onLogin(null);
        }

        checkLogin();
    });

    onDestroy(() => {
        stopCheckingLogin();
    });
</script>

<div class="pt-10 flex justify-center items-center">
    {#if qr}
        <div>
            {#if isDevelopment()}
                <ErrorBox hasDetail={true}>
                    <div>
                        You are in dev mode!
                    </div>
                    <div slot="detail">
                        Scanning the QR code in dev mode will not work!
                        <br />
                        To log in, please manually set a key in the <em>lnauth</em> table of the <em>dev</em> database!
                        <br />
                        You can do that by running <strong>./scripts/exec_lnauth.sh KEY</strong>.
                        <br />
                        PS: KEY can be anything, but it will uniquely identify your user, so if you want to test with different users, you can just pass different keys here (for different log in sessions).
                    </div>
                </ErrorBox>
            {/if}

            <Wallets />

            <QR qr={qr} protocol="lightning" address={lnurl} />
        </div>
    {:else}
        <Loading />
    {/if}
</div>
