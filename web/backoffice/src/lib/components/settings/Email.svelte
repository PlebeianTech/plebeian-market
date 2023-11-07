<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile, putVerify, type UserProfile, getProfile } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { ExternalAccountProvider } from "$lib/types/user";
    import { Info, token } from "$sharedLib/stores";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";

    export let onSave: () => void = () => {};

    let email: string | null = null;
    let phrase: string = "";

    $: isValidEmail = email !== null && email !== "";

    $: saveActive = !inRequest && $user && isValidEmail && (email !== $user.email);

    $: verifyActive = !inRequest && $user && phrase !== "";

    let checkTimeout: ReturnType<typeof setTimeout> | null = null;

    let inRequest = false;
    function save() {
        inRequest = true;
        let p: UserProfile = {};
        if (email !== null && email !== "") {
            p.email = email;
        }
        putProfile($token, p,
            (u, _) => {
                user.set(u);
                Info.set("Your email has been saved!");
                inRequest = false;
                checkTimeout = setTimeout(checkVerified, 1000);
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    function checkVerified() {
        getProfile($token, 'me', u => {
            if (u && u.emailVerified) {
                user.set(u);
                Info.set("Your email address has been verified!");
                onSave();
            } else {
                checkTimeout = setTimeout(checkVerified, 1000);
            }
        });
    }

    function verify() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Email, false, phrase,
            () => {
                user.update(u => { if (u) { u.emailVerified = true; } return u; });
                Info.set("Your email address has been verified!");
                inRequest = false;
                onSave();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    function resend() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Email, true, undefined,
            () => {
                user.update(u => { if (u) { u.emailVerificationPhraseSentAt = new Date(); } return u; });
                Info.set("Check your Email!");
                inRequest = false;
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    onMount(async () => {
        window.scrollTo(0, 0);

        if ($user) {
            email = $user.email ? $user.email : "";
        }
    });

    onDestroy(() => {
        if (checkTimeout !== null) {
            clearTimeout(checkTimeout);
        }
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>Email</li>
        </ul>
    </div>
{/if}

<div class="w-full flex items-center justify-center mt-24">
    <div class="max-w-lg">
        <InfoBox>
            To ensure you never miss a sale or an enquiry we will always use nostr DMs by default when appropriate.
            <br />
            But as a backup and for your personal preference, please add an email address.
        </InfoBox>
    </div>
</div>

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <label class="label" for="stallName">
            <span class="label-text">Email</span>
            <div class="lg:tooltip" data-tip="We use your email address to notify you of incoming orders.">
                <InfoIcon />
            </div>
        </label>
        <input bind:value={email} id="email" name="email" type="text" class="input input-bordered input-lg w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save" class="btn btn-primary btn-lg" class:btn-disabled={!saveActive} on:click|preventDefault={save}>Save</button>
</div>

{#if $user && $user.email !== null && !$user.emailVerified}
    <div class="w-full flex items-center justify-center mt-8">
        <div class="max-w-lg">
            <InfoBox>
                <span>Please enter the three BIP-39 words we sent to your email!</span>
            </InfoBox>
        </div>
    </div>
    <div class="w-full flex items-center justify-center mt-4">
        <div class="form-control w-full max-w-lg">
            <label class="label" for="title">
                <span class="label-text">Verification phrase</span>
            </label>
            <input bind:value={phrase} type="text" name="phrase" class="input input-lg input-bordered" />
        </div>
    </div>

    <div class="flex justify-center items-center mt-4 h-15 gap-5">
        <button class="btn" on:click={resend} disabled={inRequest}>Resend</button>
        <button id="verify" class="btn btn-primary btn-lg" class:btn-disabled={!verifyActive} on:click|preventDefault={verify}>Verify</button>
    </div>
{/if}
