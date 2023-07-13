<script lang="ts">
    import ResumeList from "$lib/components/resume/List.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {NostrPublicKey} from "$sharedLib/stores";
    import {waitAndShowLoginIfNotLoggedAlready} from "$sharedLib/utils";
    import {goto} from "$app/navigation";

    function goEditResume() {
        if ($NostrPublicKey) {
            goto("/p/" + $NostrPublicKey + "#edit");
        } else {
            waitAndShowLoginIfNotLoggedAlready();
        }
    }
</script>

<svelte:head>
    <title>Skills Market</title>
</svelte:head>

<Titleh1>Skills Market</Titleh1>

<div class="flex justify-center items-center">
    <a class="btn btn-primary" on:click={goEditResume} >Edit My Résumé</a>
</div>

<div class="divider"></div>

<h2 class="text-2xl lg:text-3xl fontbold mt-0 lg:mt-8 mb-2 text-center">Plebs with résumés</h2>

<ResumeList />
