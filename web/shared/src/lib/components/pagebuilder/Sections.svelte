<script lang="ts">
    import {onMount} from "svelte";
    import {isSuperAdmin, NostrGlobalConfig} from "$sharedLib/stores";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    import {getPage} from "$sharedLib/pagebuilder";
    import SectionsStalls from "$sharedLib/components/pagebuilder/SectionsStalls.svelte";
    import SectionsProducts from "$sharedLib/components/pagebuilder/SectionsProducts.svelte";
    import SectionsText from "$sharedLib/components/pagebuilder/SectionsText.svelte";
    import SectionsProductsSlider from "$sharedLib/components/pagebuilder/SectionsProductsSlider.svelte";
    import SectionsImageBanner from "$sharedLib/components/pagebuilder/SectionsImageBanner.svelte";
    import BuilderSectionSetup from "$sharedLib/components/pagebuilder/BuilderSectionSetup.svelte";
    import Edit from "$sharedLib/components/icons/Edit.svelte";

    export let pageId;

    const maxProductsLoaded = 20;

    let setupSection;
    let content = null;
    let orderedSections;
    let viewPageAnyways = false;

    $: if (Object.keys($NostrGlobalConfig).length > 0) {
        content = getPage(pageId, $NostrGlobalConfig);

        if (content?.sections) {
            orderedSections = Object.entries(content.sections).sort((a, b) => {
                return a[1].order - b[1].order;
            });
        }
    }

    onMount(async () => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        viewPageAnyways = true;
    });
</script>

{#if Object.keys($NostrGlobalConfig).length > 0 || viewPageAnyways}
    {#if content?.sections && Object.keys(content.sections).length > 0}
        <div class="pt-12">
            {#each orderedSections as [sectionId, section]}
                {#if section?.params?.sectionType && (section?.values || ['text', 'image_banner'].includes(section.params.sectionType))}
                    <div class="relative overflow-x-hidden">
                        {#if section.params.sectionType !== 'image_banner'}
                            <h2 class="text-2xl font-bold text-center mb-2 md:mb-5">
                                {section.title}
                                {#if $isSuperAdmin}
                                    <button class="btn btn-square ml-2" on:click={() => setupSection(pageId, sectionId, null, true)}>
                                        <span class="size-6"><Edit /></span>
                                    </button>
                                {/if}
                            </h2>
                        {/if}

                        {#if section?.params?.sectionType === 'text'}
                            <SectionsText {pageId} {sectionId} />
                        {:else if section?.params?.sectionType === 'stalls'}
                            <SectionsStalls {pageId} {sectionId} />
                        {:else if section?.params?.sectionType === 'products'}
                            <SectionsProducts {pageId} {sectionId} />
                        {:else if section?.params?.sectionType === 'products_with_slider'}
                            <SectionsProductsSlider {pageId} {sectionId} {setupSection} />
                        {:else if section?.params?.sectionType === 'image_banner'}
                            <SectionsImageBanner {section} />
                        {:else if section?.params?.sectionType === 'stall_products'}
                            ----- Stall Products
                        {/if}
                    </div>

                    <div class="divider w-[80%] mx-auto my-8 md:my-10"></div>
                {/if}
            {/each}
        </div>

        {#if $isSuperAdmin}
            <BuilderSectionSetup bind:setupSection={setupSection} />
        {/if}

    {:else}
        {#if pageId === 0}
            <ProductCardBrowser {maxProductsLoaded} />
        {:else}
            <div class="p-12 flex flex-wrap items-center justify-center">
                <p class="mt-8 text-3xl">No content defined for this page yet.</p>
            </div>
        {/if}
    {/if}
{:else}
    <div class="p-12 flex flex-wrap items-center justify-center">
        <span class="loading loading-bars w-64"></span>
    </div>
{/if}
