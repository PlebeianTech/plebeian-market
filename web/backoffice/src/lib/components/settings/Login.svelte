<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { ErrorHandler, putVerifyLnurl, getProfile } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { Info, token } from "$sharedLib/stores";
    import Wallets from "$lib/components/notifications/Wallets.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import QR from "$lib/components/QR.svelte";
    import ErrorBox from "$lib/components/notifications/ErrorBox.svelte";

    export let onSave: () => void = () => {};

    let hasLnauthKey: boolean = false;

    let lnurl;
    let qr;
    let k1: string | null = null;

    let inRequest = false;

    let checkTimeout: ReturnType<typeof setTimeout> | null = null;

    function stopCheckingLnurl() {
        if (checkTimeout !== null) {
            clearTimeout(checkTimeout);
        }
    }

    function checkLnurl() {
        putVerifyLnurl($token, k1,
            (response) => {
                k1 = response.k1;
                lnurl = response.lnurl;
                qr = response.qr;
                checkTimeout = setTimeout(checkLnurl, 1000);
            },
            () => {
                checkTimeout = setTimeout(checkLnurl, 1000);
            },
            async () => {
                getProfile($token, 'me', u => {
                    user.set(u);
                    if ($user) {
                        hasLnauthKey = $user.hasLnauthKey;
                        if (hasLnauthKey) {
                            Info.set("Your Lightning wallet has been verified!");
                        }
                    }
                });
            },
            new ErrorHandler(true,
                (response) => {
                    if (response.status === 400 || response.status === 410) {
                        k1 = null;
                        checkTimeout = setTimeout(checkLnurl, 1000);
                    }
                }));
    }

    onMount(async () => {
        if ($user) {
            hasLnauthKey = $user.hasLnauthKey;
        }

        if (!hasLnauthKey) {
            checkLnurl();
        }
    });

    onDestroy(() => {
        stopCheckingLnurl();
    });
</script>

<div class="text-2xl breadcrumbs">
    <ul>
        <li>Settings</li>
        <li>Login</li>
    </ul>
</div>

{#if $user}
    <h2 class="text-3xl my-4">Lightning</h2>
    {#if $user.hasLnauthKey && hasLnauthKey}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl text-center">You have a Lightning wallet linked to your account.</div>
                <div class="flex justify-center items-center gap-4 my-8">
                    <button class="btn btn-secondary" on:click={() => { hasLnauthKey = false; k1 = null; checkLnurl(); }}>Change</button>
                </div>
                <div class="text-center">You can use that wallet to log in to the Plebeian Market backend.</div>
            </div>
        </div>
    {:else}
        {#if qr}
            <div>
                <Wallets />

                <QR qr={qr} protocol="lightning" address={lnurl} />
            </div>
        {:else}
            <Loading />
        {/if}
    {/if}

    <div class="divider"></div>

    <h2 class="text-3xl my-4">Nostr</h2>
    {#if $user.nostrPublicKey}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl">Your verified Nostr public key is:</div>
                <div class="flex justify-center items-center gap-4">
                    <pre class="my-8 text-lg bg-base-300 text-center">{$user.nostrPublicKey}</pre>
                </div>
                <div>You can log in to the Plebeian Market Stall Manager using Nostr.</div>
            </div>
        </div>
    {/if}
{/if}
