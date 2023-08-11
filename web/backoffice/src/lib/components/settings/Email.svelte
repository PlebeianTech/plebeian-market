<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile, type UserProfile } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { Info, token } from "$sharedLib/stores";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";

    export let onSave: () => void = () => {};

    let email: string | null = null;

    $: isValidEmail = email !== null && email !== "";

    $: saveActive = !saving && $user && isValidEmail && (email !== $user.email);

    let saving = false;
    function save() {
        saving = true;
        let p: UserProfile = {};
        if (email !== null && email !== "") {
            p.email = email;
        }
        putProfile($token, p,
            (u, _) => {
                user.set(u);
                Info.set("Your email has been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            email = $user.email ? $user.email : "";
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
