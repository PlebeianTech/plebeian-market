<script>
    import { onMount } from 'svelte';
    import { token } from "./stores.js";

    let qr;
    let k1;

    function refreshLogin() {
        fetch(`./api/login?k1=${k1}`)
            .then(r => r.json())
            .then(r => {
                if (r.success) {
                    sessionStorage.setItem('token', r.token)
                    token.set(r.token);
                } else {
                    setTimeout(refreshLogin, 1000);
                }
            })
    }

    function getLogin() {
        fetch("./api/login")
            .then(r => r.json())
            .then(r => {
                k1 = r.k1;
                qr = r.qr;
                setTimeout(refreshLogin, 1000);
            });
    }

    onMount(async () => {
        token.set(sessionStorage.getItem('token'));
    });

</script>

{#if qr }
    <div id="qr">{@html qr}</div>
{:else }
    <button on:click={getLogin}>Enter</button>
{/if}