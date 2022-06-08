<script lang="ts">
    import { onMount } from 'svelte';
    import { getLogin } from "../services/api";
    import { token } from "../stores";
    import Loading from "./Loading.svelte";
    import QR from "./QR.svelte";

    export let onLogin = () => {};

    let lnurl;
    let qr;
    let k1;

    function doLogin() {
        getLogin(k1,
            data => {
                if (data.success) {
                    token.set(data.token);
                    localStorage.setItem('token', data.token);
                    onLogin();
                } else {
                    if (data.k1) {
                        k1 = data.k1;
                        lnurl = data.lnurl;
                        qr = data.qr;
                    }

                    setTimeout(doLogin, 1000);
                }
            });
    }

    onMount(async () => {
        if ($token) {
            onLogin();
        } else {
            doLogin();
        }
    });
</script>

<div class="pt-10 flex justify-center items-center">
    {#if qr}
        <div>
            <p class="mb-4 text-center">Scan with <a class="link" href="https://breez.technology/">Breez,</a> <a class="link" href="https://phoenix.acinq.co/">Phoenix,</a> <a class="link" href="https://thunderhub.io/">Thunderhub,</a> <a class="link" href="https://zeusln.app/">Zeus,</a> <a class="link" href="https://getalby.com/">Alby,</a> or any <a class="link" href="https://github.com/fiatjaf/lnurl-rfc#lnurl-documents" target="_blank">LNurl compatible</a> wallet to enter the marketplace.</p>

            <QR bind:qr={qr} bind:lnurl={lnurl} />
        </div>
    {:else}
        <Loading />
    {/if}
</div>