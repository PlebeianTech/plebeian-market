<script lang="ts">
    import { onMount } from 'svelte';
    import ResumeList from "$lib/components/resume/List.svelte";
    import ErrorBox from "$lib/components/notifications/ErrorBox.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";

    let userPubKey: string | undefined = undefined;

    let loadingPubKey = true;
    async function getPubKey() {
        loadingPubKey = true;
        userPubKey = await (window as any).nostr.getPublicKey();
        loadingPubKey = false;
    }

    onMount(async () => getPubKey());
</script>

<svelte:head>
    <title>Skills Market</title>
</svelte:head>

<Titleh1>Skills Market</Titleh1>

<div class="flex justify-center items-center">
    {#if userPubKey}
        <a class="btn btn-primary" href="/p/{userPubKey}#edit">Edit My Résumé</a>
    {:else if !loadingPubKey}
        <ErrorBox>
            Please use a browser extension to access Nostr.
        </ErrorBox>
    {/if}
</div>

<div class="divider"></div>

<h2 class="text-2xl lg:text-3xl fontbold mt-0 lg:mt-8 mb-2 text-center">Plebs with résumés</h2>

<ResumeList />
