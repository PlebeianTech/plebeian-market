<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchAPI } from "../services/api";
    import { token } from "../stores";
    import Loading from "./Loading.svelte";

    export let onLogin = () => {};

    let lnurl;
    let qr;
    let k1;

    let copied = false;
    function copy() {
        navigator.clipboard.writeText(lnurl);
        copied = true;
    }

    function getLogin() {
        fetchAPI("/login" + (k1 ? `?k1=${k1}` : ""), 'GET', null, null,
            (r) => {
                if (r.status === 200) {
                    r.json().then(
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

                                setTimeout(getLogin, 1000);
                            }
                        }
                    );
                }
            });
    }

    onMount(async () => {
        if ($token) {
            onLogin();
        } else {
            getLogin();
        }
    });
</script>

<div class="pt-10 flex justify-center items-center">
    {#if qr}
        <div>
            <p class="mb-4">Scan with a <a class="link" href="https://github.com/fiatjaf/lnurl-rfc#lnurl-documents" target="_blank">compatible</a> wallet to log in.</p>
            <div class="qr glowbox">{@html qr}</div>
            <div class="mt-10 flex justify-center items-center">
                <input value={lnurl} type="text" class="input input-bordered w-full max-w-xs" disabled />
                <button class="btn ml-2 w-20" on:click={copy}>{#if copied}Copied{:else}Copy!{/if}</button>
            </div>
        </div>
    {:else}
        <Loading />
    {/if}
</div>