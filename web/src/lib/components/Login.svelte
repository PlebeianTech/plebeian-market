<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchAPI } from "../services/api";
    import { token } from "../stores";
    import Loading from "./Loading.svelte";

    export let onLogin = () => {};

    let qr;
    let k1;

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
        <div class="qr glowbox">{@html qr}</div>
    {:else}
        <Loading />
    {/if}
</div>