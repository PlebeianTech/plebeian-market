<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { ErrorHandler, putVerifyLnurl, getProfile, putMigrate, putProfile, type UserProfile } from "$lib/services/api";
    import { user } from "$lib/stores";
    import Wallets from "$lib/components/notifications/Wallets.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import QR from "$lib/components/QR.svelte";
    import { Info, token, Error } from "$sharedLib/stores";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";

    let hasLnauthKey: boolean = false;
    let lnauthKeyName: string | null = null;

    let lnurl;
    let qr;
    let k1: string | null = null;

    export function skip() {
        putProfile($token, {lnauthKeyName: ""}, (u, _) => { user.set(u); });
    }

    let checkTimeout: ReturnType<typeof setTimeout> | null = null;

    function stopCheckingLnurl() {
        if (checkTimeout !== null) {
            clearTimeout(checkTimeout);
        }
    }

    let userExists = false;

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
                            putProfile($token, {lnauthKeyName: null}, (u, _) => { user.set(u); lnauthKeyName = null; });
                        }
                    }
                });
            },
            new ErrorHandler(false,
                (response) => {
                    response.json().then(
                        data => {
                            if (data.user_exists) {
                                userExists = true;
                            } else if (data.message) {
                                Error.set(data.message);

                                if (response.status === 400 || response.status === 410) {
                                    k1 = null;
                                    checkTimeout = setTimeout(checkLnurl, 1000);
                                }
                            }
                        });
                }));
    }

    let migrating = false;
    function migrate() {
        migrating = true;
        putMigrate($token,
            () => {
                Info.set("User migration complete!");
                migrating = false;
                userExists = false;
                getProfile($token, 'me', u => {
                    user.set(u);
                    if ($user) {
                        hasLnauthKey = $user.hasLnauthKey;
                        if (hasLnauthKey) {
                            Info.set("Your Lightning wallet has been verified!");
                            putProfile($token, {lnauthKeyName: null}, (u, _) => { user.set(u); lnauthKeyName = null; });
                        }
                    }
                });
            },
            new ErrorHandler(true, (_) => { migrating = false; }));
    }

    let savingKeyName = false;
    function saveKeyName() {
        savingKeyName = true;
        let p: UserProfile = {};
        if (lnauthKeyName !== null) {
            p.lnauthKeyName = lnauthKeyName;
        } else {
            p.lnauthKeyName = "";
        }
        putProfile($token, p,
            (u, _) => {
                user.set(u);
                lnauthKeyName = u.lnauthKeyName;
                Info.set("Your lightning key has been saved!");
                savingKeyName = false;
            },
            new ErrorHandler(true, () => savingKeyName = false));
    }

    onMount(async () => {
        if ($user) {
            hasLnauthKey = $user.hasLnauthKey;
            lnauthKeyName = $user.lnauthKeyName;
        }

        if (!hasLnauthKey) {
            checkLnurl();
        }
    });

    onDestroy(() => {
        stopCheckingLnurl();
    });
</script>

{#if $user && $user.hasLnauthKey && hasLnauthKey}
    {#if $user.lnauthKeyName !== null}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl text-center">You have a Lightning wallet linked to your account{#if $user.lnauthKeyName !== ""}:{:else}.{/if}</div>
                {#if $user.lnauthKeyName !== ""}
                    <pre class="my-8 text-lg bg-base-300 text-center">{$user.lnauthKeyName}</pre>
                {/if}
                <div class="flex justify-center items-center gap-4 my-8">
                    <button class="btn btn-secondary" on:click={() => { hasLnauthKey = false; k1 = null; checkLnurl(); }}>Change</button>
                </div>
                <div class="text-center">You can log in to the Plebeian Market Stall Manager using Lightning.</div>
            </div>
        </div>
    {:else}
        <div class="w-full flex items-center justify-center mt-8">
            <div class="form-control w-full max-w-lg">
                <label class="label" for="lnauthKeyName">
                    <span class="label-text">Key name (optional)</span>
                    <div class="lg:tooltip" data-tip="Give your key a name. This will later help you remember which wallet you used, if you have multiple.">
                        <InfoIcon />
                    </div>
                </label>
                <input bind:value={lnauthKeyName} id="lnauthKeyName" name="lnauthKeyName" type="text" class="input input-bordered input-lg w-full" />
                <button class="btn btn-secondary mt-4" class:btn-disabled={savingKeyName} on:click={saveKeyName}>Save</button>
            </div>
        </div>
    {/if}
{:else}
    {#if userExists}
        <p class="text-3xl my-4">An old-style user with this Lightning log in already exists!</p>
        <button class="btn btn-secondary" class:btn-disabled={migrating} on:click={migrate}>Import user</button>
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
