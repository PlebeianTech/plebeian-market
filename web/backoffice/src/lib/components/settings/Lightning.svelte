<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { ErrorHandler, putVerifyLnurl, getProfile } from "$lib/services/api";
    import { user, token, Info } from "$lib/stores";
    import Wallets from "$lib/components/notifications/Wallets.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import QR from "$lib/components/QR.svelte";

    export let onSave: () => void = () => {};

    let hasLnauthKey: boolean = false;

    let lnurl;
    let qr;
    let k1: string | null = null;

    let checkTimeout: ReturnType<typeof setTimeout> | null = null;

    function stopChecking() {
        if (checkTimeout !== null) {
            clearTimeout(checkTimeout);
        }
    }

    function check() {
        putVerifyLnurl($token, k1,
            (response) => {
                k1 = response.k1;
                lnurl = response.lnurl;
                qr = response.qr;
                checkTimeout = setTimeout(check, 1000);
            },
            () => {
                checkTimeout = setTimeout(check, 1000);
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
                        checkTimeout = setTimeout(check, 1000);
                    }
                }));
    }

    onMount(async () => {
        if ($user) {
            hasLnauthKey = $user.hasLnauthKey;
        }

        if (!hasLnauthKey) {
            check();
        }
    });

    onDestroy(() => {
        stopChecking();
    });
</script>

<div class="text-2xl breadcrumbs">
    <ul>
        <li>Settings</li>
        <li>Lightning</li>
    </ul>
</div>

{#if $user}
    {#if $user.hasLnauthKey && hasLnauthKey}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl text-center">You have a Lightning wallet linked to your account.</div>
                <div class="flex justify-center items-center gap-4 my-8">
                    <button class="btn btn-secondary" on:click={() => { hasLnauthKey = false; k1 = null; check(); }}>Change</button>
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
{/if}
