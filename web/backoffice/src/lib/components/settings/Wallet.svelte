<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile, type UserProfile } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { Info, token } from "$sharedLib/stores";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";

    export let onSave: () => void = () => {};

    let wallet: string | null = null;
    let walletName: string | null = null;
    let lightningAddress: string | null = null;

    $: isValidLightningAddress = lightningAddress !== null && lightningAddress !== "";
    $: isValidWallet = wallet !== null && wallet !== "";

    $: saveActive = !saving && $user && isValidLightningAddress && isValidWallet && (lightningAddress !== $user.lightningAddress || wallet !== $user.wallet || walletName !== $user.walletName);

    let saving = false;
    function save() {
        saving = true;
        let p: UserProfile = {};
        if (wallet !== null) {
            p.wallet = wallet;
        }
        if (walletName !== null) {
            p.walletName = walletName;
        }
        if (lightningAddress !== null) {
            p.lightningAddress = lightningAddress;
        }
        putProfile($token, p,
            (u, _) => {
                user.set(u);
                Info.set("Your wallet information has been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        window.scrollTo(0, 0);

        if ($user) {
            wallet = $user.wallet ? $user.wallet : "";
            walletName = $user.walletName ? $user.walletName : "";
            lightningAddress = $user.lightningAddress ? $user.lightningAddress : "";
        }
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>Wallet</li>
        </ul>
    </div>
{/if}

<div class="w-full flex items-center justify-center mt-24">
    <div class="max-w-lg">
        <InfoBox>
            Plebeian Market doesn't hold your money. You need to use a separate wallet for that purpose!
        </InfoBox>
    </div>
</div>

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <label class="label" for="stallName">
            <span class="label-text">Lightning address</span>
            <div class="lg:tooltip" data-tip="A lightning address looks similar to an email address and is offered by wallets such as Wallet of Satoshi or Alby or websites like Stacker News.">
                <InfoIcon />
            </div>
        </label>
        <input bind:value={lightningAddress} id="lightningAddress" name="lightningAddress" type="text" class="input input-bordered input-lg w-full" placeholder="eg: [YourUserName]@walletofsatoshi.com" />
    </div>
</div>

<div class="w-full flex items-center justify-center mt-8">
    <div class="w-full max-w-lg">
        <div class="divider"></div>
    </div>
</div>

<div class="w-full flex items-center justify-center">
    <div class="max-w-lg">
        <div class="alert shadow-lg">
            We use the XPUB to generate addresses for larger payments but also for buyers that simply don't have a Lightning wallet.
        </div>
    </div>
</div>

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <label class="label" for="wallet">
            <span class="label-text">XPUB / ZPUB <a href="/faq?question=xpub" target="_blank" class="lg:tooltip" data-tip="Click to read: How do I get the XPUB/YPUB/ZPUB from my wallet?">?</a></span>
            <div class="lg:tooltip" data-tip="Non-custodial wallets such as Blue Wallet offer you an XPUB and are a great way to get started with accepting Bitcoin payments.">
                <InfoIcon />
            </div>
        </label>
        <input bind:value={wallet} id="wallet" name="wallet" type="text" class="input input-bordered input-lg w-full" />
    </div>
</div>

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <label class="label" for="walletName">
            <span class="label-text">Wallet name (optional)</span>
            <div class="lg:tooltip" data-tip="Give your wallet a name. This will later help you remember which wallet you used, if you have multiple.">
                <InfoIcon />
            </div>
        </label>
        <input bind:value={walletName} id="walletName" name="walletName" type="text" class="input input-bordered input-lg w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save" class="btn btn-primary btn-lg" class:btn-disabled={!saveActive} on:click|preventDefault={save}>Save</button>
</div>
