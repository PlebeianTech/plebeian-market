<svelte:head>
    <title>Skills Market</title>
</svelte:head>

<script lang="ts">
    import ResumeEditor from "$lib/components/resume/Editor.svelte";
    import ResumeList from "$lib/components/resume/List.svelte";
    import ResumeViewer from "$lib/components/resume/Viewer.svelte";
    import type { UserResume } from "$lib/types/user";

    let editing = false;
    let viewingResume: UserResume | null = null;
</script>

<div class="px-2 pb-14 mx-auto w-screen lg:w-2/3">
    <h1 class="text-3xl lg:text-6xl fontbold mt-0 lg:mt-8 mb-2">Skills Market</h1>

    {#if editing}
        <ResumeEditor onEditFinished={() => editing = false} />
    {:else if viewingResume}
        <ResumeViewer resume={viewingResume} onViewFinished={() => viewingResume = null} />
    {:else}
        <div class="flex justify-center items-center">
            <button class="btn btn-lg btn-primary" on:click={() => editing = true}>Edit Résumé</button>
        </div>

        <h2 class="text-xl lg:text-3xl fontbold mt-0 lg:mt-8 mb-2">Plebs available for hire</h2>

        <ResumeList onView={(r) => viewingResume = r} />
    {/if}
</div>
