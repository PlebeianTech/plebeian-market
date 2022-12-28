<script lang="ts">
    import { onMount } from 'svelte';
    import { getLogin, type GetLoginInitialResponse, type GetLoginSuccessResponse } from "../services/api";
    import { token } from "../stores";
    import Loading from "./Loading.svelte";
    import QR from "./QR.svelte";
    import { isDevelopment } from "../utils";
    import type { User } from "../types/user";
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    export let onLogin = (user: User | null) => {};

    let lnurl;
    let qr;
    let k1;

    let checkLoginTimeout = null;

    export function stopCheckingLogin() {
        clearTimeout(checkLoginTimeout);
    }
    export function startCheckingLogin() {
        doLogin();
    }

    function doLogin() {
        getLogin(k1,
            (response) => {
                k1 = response.k1;
                lnurl = response.lnurl;
                qr = response.qr;
                checkLoginTimeout = setTimeout(doLogin, 1000);
            },
            () => {
                checkLoginTimeout = setTimeout(doLogin, 1000);
            },
            (response) => {
                token.set(response.token);
                localStorage.setItem('token', response.token);
                dispatch('loginEvent', {})
                onLogin(response.user);
            });
    }

    onMount(async () => {
        if ($token) {
            onLogin(null);
        }
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
            <p class="mb-0 text-center">Scan with <a class="link" href="https://breez.technology/" target="_blank">Breez</a> or
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
