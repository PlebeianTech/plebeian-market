<script>
    import { onDestroy } from 'svelte';
    import { token } from "./common.js";

    let qr;
    let k1;

    function getLogin() {
        fetch("/api/login" + (k1 ? `?k1=${k1}` : ""))
            .then(r => {
                if (r.status === 200) {
                    r.json().then(
                        data => {
                            if (data.success) {
                                token.set(data.token);
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

    const unsubscribe = token.subscribe(value => {
        if (value) {
            sessionStorage.setItem('token', value);
        } else {
            sessionStorage.removeItem('token');
            qr = k1 = null;
        }
    });
	onDestroy(unsubscribe);
</script>

{#if qr }
    <div class="qr glow-box">{@html qr}</div>
{:else }
    <div class="glowbutton glowbutton-enter" on:click|preventDefault={getLogin}></div>
{/if}