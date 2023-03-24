<svelte:head>
    <title>Skills Market</title>
</svelte:head>

<script lang="ts">
    import { onMount } from 'svelte';
    import ResumeList from "$lib/components/resume/List.svelte";

    let userPubKey;

    onMount(
        async () => {
            userPubKey = await window.nostr.getPublicKey();
        }
    );
</script>

<div class="py-3 lg:pb-14 mx-auto w-screen lg:w-2/3">
    <h1 class="text-3xl lg:text-6xl fontbold mt-0 lg:mt-2 mb-4 text-center">Skills Market</h1>

    <div class="flex justify-center items-center">
        {#if userPubKey}
            <a class="btn btn-primary" href="/p/{userPubKey}#edit">Edit My Résumé</a>
        {/if}
    </div>

    <div class="divider"></div>

    <h2 class="text-2xl lg:text-3xl fontbold mt-0 lg:mt-8 mb-2 text-center">Plebs with résumés</h2>

    <ResumeList />
</div>
