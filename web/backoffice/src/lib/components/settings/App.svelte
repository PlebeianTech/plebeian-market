<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from "$app/stores";
    import { ErrorHandler, getStatus, putUpdate } from "$lib/services/api";
    import { Info, token } from "$sharedLib/stores";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";
    import ErrorBox from "$lib/components/notifications/ErrorBox.svelte";

    export let onSave: () => void = () => {};

    let version: string | null = null;
    let lastVersion: string | null = null;
    let githubRepoUrl: string | null = null;

    let updateRequested: boolean | null = null;
    let updateRunning: boolean | null = null;
    let updateSuccess: boolean | null = null;
    let updateFailed: boolean | null = null;

    let inRequest = false;
    function update() {
        inRequest = true;
        putUpdate($token,
            () => {
                Info.set("Update requested!");
                inRequest = false;
                checkStatus(false);
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    let updateButtonActive = lastVersion !== null && version !== lastVersion && !inRequest && !updateRequested && !updateRunning;

    function checkStatus(checkLastRelease: boolean) {
        getStatus(checkLastRelease,
            (v, lv, g, ureq, urunning, usuccess, ufailed) => {
                version = v;
                lastVersion = lv;
                githubRepoUrl = g;
                updateRequested = ureq;
                updateRunning = urunning;
                updateSuccess = usuccess;
                updateFailed = ufailed;

                if (updateRequested || updateRunning) {
                    setTimeout(() => { checkStatus(false); }, 1000);
                }
            });
    }

    onMount(async () => {
        checkStatus(true);
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>App</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">App</h2>
{/if}

{#if version !== null && version !== ""}
    <div class="items-center justify-center mt-8">
        <p class="text-2xl mb-4">You are currently running<br /><strong>Plebeian Market {version}</strong>.</p>
        {#if lastVersion !== null}
            {#if version === lastVersion}
                <p class="text-xl my-4">This is the most recent version. All is well!</p>
            {:else}
                <p class="text-2xl my-4">The last available version is <strong>{lastVersion}</strong>.</p>
                {#if githubRepoUrl !== null}
                    <p class="text-xl my-4">See what is new <a class="link" target="_blank" href="{githubRepoUrl}/releases/">here</a>!</p>
                {/if}
            {/if}
        {/if}
        {#if updateRequested}
            <p class="text-2xl font-bold mt-4">You requested an update. Please wait...</p>
        {/if}
        {#if updateRunning}
            <p class="text-2xl font-bold mt-4">Update running! Please wait...</p>
        {/if}
        {#if updateSuccess}
            <InfoBox>
                Update successful!
            </InfoBox>
        {/if}
        {#if updateFailed}
            <ErrorBox>
                Update failed!
            </ErrorBox>
        {/if}
    </div>
    <div class="flex justify-center items-center mt-8 h-15">
        <button id="update-pm" class="btn btn-primary" class:btn-disabled={!updateButtonActive} on:click|preventDefault={update}>Update</button>
    </div>
{:else}
    <div class="items-center justify-center mt-8">
        <p class="text-2xl">Running <strong>Plebeian Market</strong>.</p>
    </div>
{/if}