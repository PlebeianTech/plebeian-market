<script lang="ts">
    import { onMount } from 'svelte';
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    export let onSave: () => void = () => {};

    let twitterUsername: string | null = null;

    $: isValidInput = twitterUsername !== null && twitterUsername !== "";
    $: saveButtonActive = $user && isValidInput && !saving && twitterUsername !== $user.twitterUsername;

    let saving = false;
    function save() {
        if (!twitterUsername) {
            // this would happen if somebody tries to call save when isValidInput is false
            return;
        }
        saving = true;
        putProfile($token, {twitterUsername},
            u => {
                user.set(u);
                Info.set("Your Twitter username has been saved!");
                saving = false;
                onSave();

                if ($page.url.pathname === "/") {
                    goto(`/stall/${u.nym}`);
                }
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            twitterUsername = $user.twitterUsername || "";
        }
    });
</script>

{#if !($user && $user.twitterUsername)}
    <div class="alert alert-info shadow-lg">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>We use your Twitter account to start the auctions. We DO NOT collect any personal information.</span>
        </div>
    </div>
{:else}
    {#if $page.url.pathname === "/admin/account/settings"}
        <div class="text-2xl breadcrumbs">
            <ul>
                <li>Settings</li>
                <li>Twitter</li>
            </ul>
        </div>
    {:else}
        <h2 class="text-2xl">Twitter</h2>
    {/if}
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full max-w-lg">
        <div class="z-0 translate-y-9 translate-x-2">
            <span>@</span>
        </div>
        <input bind:value={twitterUsername} id="twitter-username" name="twitter-username" type="text" class="bg-transparent z-10 ml-1.5 input input-bordered input-md w-full" />
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save-profile" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={save}>Save</button>
</div>
