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
    let viewingResumeName: string | null = null;
    let viewingResumePicture: string | null = null;
</script>

<div class="px-2 pb-4 lg:pb-14 mx-auto w-screen lg:w-2/3 p-2 py-7">
    <h1 class="text-3xl lg:text-6xl fontbold mt-0 lg:mt-8 mb-2 text-center">Skills Market</h1>

    {#if editing}
        <ResumeEditor onEditFinished={() => editing = false} />
    {:else if viewingResume}
        <ResumeViewer resume={viewingResume} name={viewingResumeName} picture={viewingResumePicture} onViewFinished={() => viewingResume = null} />
    {:else}
        <div class="flex justify-center items-center">
            <button class="btn btn-lg btn-primary" on:click={() => editing = true}>Edit Résumé</button>
        </div>

        <div class="divider"></div>
        <h2 class="text-2xl lg:text-3xl fontbold mt-0 lg:mt-8 mb-2 text-center">Plebs with résumés</h2>

        <ResumeList onView={(r, n, p) => { viewingResume = r; viewingResumeName = n; viewingResumePicture = p; } } />
    {/if}
</div>
