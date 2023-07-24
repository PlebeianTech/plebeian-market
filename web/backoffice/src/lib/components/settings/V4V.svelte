<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";

    export let onSave: () => void = () => {};

    let contributionPercent;

    const CONTRIBUTION_PERCENT_DEFAULT = 5.0; // NB: must be in sync with the value in config.py

    $: saveButtonActive = $user && !saving && contributionPercent !== $user.contributionPercent;

    let saving = false;
    function save() {
        saving = true;
        putProfile($token, {contributionPercent},
            (u, _) => {
                user.set(u);
                if (contributionPercent === 0) {
                    Info.set("You cheapskate!");
                } else if (contributionPercent < 3) {
                    Info.set("Better than nothing!");
                } else if (contributionPercent < 5) {
                    Info.set("Thank you for your contribution!");
                } else {
                    Info.set("We love you too!");
                }
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            contributionPercent = $user.contributionPercent !== null ? $user.contributionPercent : CONTRIBUTION_PERCENT_DEFAULT;
        }
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>Value 4 Value</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">Value 4 Value</h2>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div>
        <div class="form-control w-full max-w-lg">
            <label class="label" for="contribution-percent">
                <span class="label-text">Value4Value contribution</span>
            </label>
            <div>
                <input type="range" min="0" max="5" bind:value={contributionPercent} class="range" step="0.5" />
                <div class="w-full flex justify-between text-xs px-2">
                <span>|</span>
                <span>|</span>
                <span>|</span>
                <span>|</span>
                <span>|</span>
                <span>|</span>
                </div>
            </div>
            <label class="label" for="contribution-percent">
                <span class="label-text w-2/4">Generosity enables us to continue creating free and open source solutions!</span>
                <span class="label-text text-right w-2/4">100% goes to powering the Bitcoin movement!</span>
            </label>
        </div>

        <div class="text-2xl text-center">
            { contributionPercent }%
        </div>

        <div class="text-4xl text-center">
            {#if contributionPercent === 0}
                {@html "&#x1F4A9;"}
            {:else if contributionPercent < 2}
                {@html "&#x1F625;"}
            {:else if contributionPercent < 3}
                {@html "&#x1F615;"}
            {:else if contributionPercent < 4}
                {@html "&#x1F610;"}
            {:else if contributionPercent <= 4.5}
                {@html "&#x1F642;"}
            {:else if contributionPercent <= 5}
                {@html "&#x1F60D;"}
            {/if}
        </div>
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save-profile" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={save}>Save</button>
</div>