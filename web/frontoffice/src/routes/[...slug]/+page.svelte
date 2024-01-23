<script>
    import Sections from "$lib/components/pagebuilder/Sections.svelte";
    import {getPage, getPageIdForSlug} from "$lib/pagebuilder";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {NostrGlobalConfig} from "$sharedLib/stores";
    import {onMount} from "svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    let pageIdForSlug = -1;
    let page = null;

    onMount(async () => {
        let unusedHackToFireReactivity = $NostrGlobalConfig;
        pageIdForSlug = getPageIdForSlug(data.slug);
        page = getPage(pageIdForSlug);
    });
</script>

<svelte:head>
    <title>{page?.title ?? ''}</title>
</svelte:head>

{#if pageIdForSlug === -1}
    <div class="p-12 flex flex-wrap items-center justify-center">
        <span class="loading loading-bars w-64"></span>
    </div>
{:else if !pageIdForSlug}
    <p class="text-3xl items-center justify-center flex mt-20">404 page. Not found.</p>
{:else}
    {#if page.title && (page?.showTitle ?? true)}
        <Titleh1>{page.title}</Titleh1>
    {/if}

    <Sections pageId={pageIdForSlug} />
{/if}
