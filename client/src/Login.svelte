<script>
    import { onDestroy } from 'svelte';
    import { token, ContributionPercent, TwitterUsername, TwitterUsernameVerified, fetchAPI } from "./common.js";

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
                                ContributionPercent.set(data.user.contribution_percent);
                                TwitterUsername.set(data.user.twitter_username);
                                TwitterUsernameVerified.set(data.user.twitter_username_verified);
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

<div class="pt-10 flex justify-center items-center">
    {#if qr}
        <div class="qr glowbox">{@html qr}</div>
    {:else}
        <div class="glowbutton glowbutton-enter" on:click|preventDefault={getLogin}></div>
    {/if}
</div>