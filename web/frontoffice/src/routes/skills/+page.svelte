<script lang="ts">
    import { onMount } from 'svelte';
    import ResumeList from "$lib/components/resume/List.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {NostrPublicKey} from "$lib/stores";
    import {waitAndShowLoginIfNotLoggedAlready} from "$lib/utils";

    onMount(async () => {
        waitAndShowLoginIfNotLoggedAlready();
    });
</script>

<svelte:head>
    <title>Skills Market</title>
</svelte:head>

<Titleh1>Skills Market</Titleh1>

<div class="flex justify-center items-center">
    {#if $NostrPublicKey}
        <a class="btn btn-primary" href="/p/{$NostrPublicKey}#edit">Edit My Résumé</a>
    {/if}
</div>

<div class="divider"></div>

<h2 class="text-2xl lg:text-3xl fontbold mt-0 lg:mt-8 mb-2 text-center">Plebs with résumés</h2>

<ResumeList />
