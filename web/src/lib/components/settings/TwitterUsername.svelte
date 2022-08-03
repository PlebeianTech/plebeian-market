<script lang="ts">
    import { onMount } from 'svelte';
    import { ErrorHandler, postProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";

    export let onSave: () => void = () => {};

    let twitterUsername: string | null = null;

    $: isValidInput = twitterUsername !== null && twitterUsername !== "";
    $: saveButtonActive = $user && isValidInput && !saving && twitterUsername !== $user.twitter.username;

    let saving = false;
    function save() {
        if (!twitterUsername) {
            // this would happen if somebody tries to call save when isValidInput is false
            return;
        }
        saving = true;
        postProfile($token, {twitterUsername},
            u => {
                user.set(u);
                Info.set("Your Twitter username has been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            twitterUsername = $user.twitter.username ? `${$user.twitter.username}` : "";
        }
    });
</script>

{#if !($user && $user.twitter.username)}
    <div class="alert alert-info shadow-lg">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>We use your Twitter account to start the auctions. We DO NOT collect any personal information.</span>
        </div>
    </div>
{:else}
    <div class="alert shadow-lg">
        <div>
            <span>Twitter</span>
        </div>
    </div>
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
    {#if saveButtonActive}
        <div id="save-profile" class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>
