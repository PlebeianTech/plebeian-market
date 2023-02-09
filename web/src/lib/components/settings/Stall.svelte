<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import MarkdownEditor from "$lib/components/MarkdownEditor.svelte";

    export let onSave: () => void = () => {};

    let nym: string | null = null;
    let stallName: string = "";
    let stallDescription: string = "";

    $: saveButtonActive = $user && !saving && nym !== null && nym !== "" && (nym !== $user.nym || stallName !== $user.stallName || stallDescription !== $user.stallDescription);

    let saving = false;
    function save() {
        if (nym === null || nym === "") {
            return;
        }
        saving = true;
        putProfile($token, {nym, stallName, stallDescription},
            u => {
                user.set(u);
                Info.set("Your stall details have been saved!");
                nym = u.nym || "";
                stallName = u.stallName || "";
                stallDescription = u.stallDescription || "";
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            nym = $user.nym;
            stallName = $user.stallName || "";
            stallDescription = $user.stallDescription || "";
        }
    });
</script>

{#if $page.url.pathname === "/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>My Stall</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">My Stall</h2>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full">
        <label class="label" for="stallName">
            <span class="label-text">Title</span>
        </label>
        <input bind:value={stallName} id="stallName" name="stallName" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>

<MarkdownEditor bind:value={stallDescription} />

<div class="alert alert-info shadow-lg mt-4">
    <div>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span>Your nym is what uniquely identifies you on plebeian.market.</span>
    </div>
</div>

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full">
        <label class="label" for="nym">
            <span class="label-text">Nym</span>
        </label>
        <input bind:value={nym} id="nym" name="nym" type="text" class="input input-bordered input-md w-full" style="text-transform: lowercase" />
    </div>
</div>

{#if $user && nym && nym !== $user.nym}
    <div class="alert alert-warning shadow-lg mt-4">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <div>
                <p class="text-xs">Note: Your nym is also part of your stall's public URL.</p>
                <p class="text-xs mt-1">Changing your nym will make links to your stall look like this: <strong>https://plebeian.market/stall/{nym.trim().toLowerCase()}</strong></p>
                <p class="text-xs mt-1">If you have shared links to your stall with others, you will have to share them again!</p>
            </div>
        </div>
    </div>
{/if}

<div class="flex justify-center items-center mt-4 h-15">
    {#if saveButtonActive}
        <button id="save-profile" class="btn btn-primary" on:click|preventDefault={save}>Save</button>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>
