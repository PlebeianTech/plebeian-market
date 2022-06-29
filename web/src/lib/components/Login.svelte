<script lang="ts">
    import { onMount } from 'svelte';
    import { getLogin, type GetLoginInitialResponse, type GetLoginSuccessResponse } from "../services/api";
    import { token } from "../stores";
    import Loading from "./Loading.svelte";
    import QR from "./QR.svelte";
    import type { User } from "../types/user";

    export let onLogin = (user: User | null) => {};

    let lnurl;
    let qr;
    let k1;

    function doLogin() {
        getLogin(k1,
            (response) => {
                k1 = response.k1;
                lnurl = response.lnurl;
                qr = response.qr;
                setTimeout(doLogin, 1000);
            },
            () => {
                setTimeout(doLogin, 1000);
            },
            (response) => {
                token.set(response.token);
                localStorage.setItem('token', response.token);
                onLogin(response.user);
            });
    }

    onMount(async () => {
        if ($token) {
            onLogin(null);
        } else {
            doLogin();
        }
    });
</script>

<div class="pt-10 flex justify-center items-center">
    {#if qr}
        <div>
            <p class="mb-4 text-center">Scan with <a class="link" href="https://breez.technology/">Breez,</a>
                <a class="link" href="https://phoenix.acinq.co/">Phoenix,</a>
                <a class="link" href="https://zeusln.app/">Zeus,</a>
                </p>
                <p class="mb-4 text-center">or use <a class="link" href="https://getalby.com/">Alby,</a>
                    <a class="link" href="https://thunderhub.io/">Thunderhub</a>
                    or any <a class="link" href="https://github.com/fiatjaf/lnurl-rfc#lnurl-documents" target="_blank">
                        LNurl compatible wallet </a> to enter the marketplace.</p>

            <QR bind:qr={qr} bind:lnurl={lnurl} />
        </div>
    {:else}
        <Loading />
    {/if}
</div>