<script lang="ts">
    import { onMount, onDestroy, createEventDispatcher } from 'svelte';
    import { loginLnurl } from "$lib/services/api";
    import { token, user } from "$lib/stores";
    import Loading from "$lib/components/Loading.svelte";
    import QR from "$lib/components/QR.svelte";
    import { isDevelopment } from "$lib/utils";
    import type { User } from "$lib/types/user";

    const dispatch = createEventDispatcher();

    export let onLogin: (user: User | null) => void = (_) => {};

    let lnurl;
    let qr;
    let k1: string | null = null;

    let checkLoginTimeout: ReturnType<typeof setTimeout> | null = null;

    export function stopCheckingLogin() {
        if (checkLoginTimeout !== null) {
            clearTimeout(checkLoginTimeout);
        }
        k1 = null;  // k1 cannot be used again if logout is done
    }

    export function startCheckingLogin() {
        loginLnurl(k1,
            (response) => {
                k1 = response.k1;
                lnurl = response.lnurl;
                qr = response.qr;
                checkLoginTimeout = setTimeout(startCheckingLogin, 1000);
            },
            () => {
                checkLoginTimeout = setTimeout(startCheckingLogin, 1000);
            },
            async (response) => {
                token.set(response.token);
                localStorage.setItem('token', response.token);
                dispatch('login', {})

                while ($user === null) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }

                onLogin(response.user);
            },
            () => {
                dispatch('loginTokenExpiredEvent', {})
            });
    }

    onMount(async () => {
        if ($token) {
            onLogin(null);
        }

        startCheckingLogin();
    });

    onDestroy(() => {
        stopCheckingLogin();
    });
</script>

<div class="pt-10 flex justify-center items-center">
    {#if qr}
        <div>
            {#if isDevelopment()}
                <div class="alert alert-error shadow-lg mb-4">
                    <div>
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                            NOTE: Scanning the QR code in dev mode will not work!
                            <br />
                            To log in, please manually set a key in the <em>lnauth</em> table of the <em>dev</em> database!
                            <br />
                            You can do that by running <strong>./scripts/exec_lnauth.sh KEY</strong>.
                            <br />
                            PS: KEY can be anything, but it will uniquely identify your user, so if you want to test with different users, you can just pass different keys here (for different log in sessions).
                        </div>
                    </div>
                </div>
            {/if}
            <h1 class="text-2xl mb-4 text-center"><b>Login to Plebeian Market</b></h1>
            <p class="mb-0 text-center">Scan with <a class="link" href="https://breez.technology/" target="_blank" rel="noreferrer">Breez</a> or
                <a class="link" href="https://zeusln.app/" target="_blank" rel="noreferrer">Zeus,</a> or use
                <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a>,
            </p>
            <p class="mb-4 text-center">
                <a class="link" href="https://thunderhub.io/" target="_blank" rel="noreferrer">ThunderHub</a>,
                <a class="link" href="https://sparrowwallet.com/" target="_blank" rel="noreferrer">Sparrow</a>
                or any <a class="link" href="https://github.com/fiatjaf/lnurl-rfc#lnurl-documents" target="_blank" rel="noreferrer">
                    LNurl compatible wallet</a> to enter the marketplace.
            </p>

            <QR qr={qr} protocol="lightning" address={lnurl} />
        </div>
    {:else}
        <Loading />
    {/if}
</div>
