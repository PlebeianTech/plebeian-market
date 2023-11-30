<script lang="ts">
    import {isSuperAdmin, NostrGlobalConfig} from "$sharedLib/stores";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    import {getPage} from "$lib/pagebuilder";
    import SectionsStalls from "$lib/components/pagebuilder/SectionsStalls.svelte";
    import SectionsProducts from "$lib/components/pagebuilder/SectionsProducts.svelte";
    import SectionsText from "$lib/components/pagebuilder/SectionsText.svelte";
    import SectionsProductsSlider from "$lib/components/pagebuilder/SectionsProductsSlider.svelte";
    import Edit from "$sharedLib/components/icons/Edit.svelte";
    import BuilderSectionSetup from "$lib/components/pagebuilder/BuilderSectionSetup.svelte";

    export let pageId;

    const maxProductsLoaded = 20;

    let content = null;
    let orderedSections;

    $: { content = getPage(pageId, $NostrGlobalConfig); }

    $: if (content && content.sections) {
        orderedSections = Object.entries(content.sections).sort((a, b) => {
            return a[1].order - b[1].order;
        });
    }

    let setupSection;
</script>

{#if content && Object.keys(content.sections).length > 0}
    <div class="pt-12">
        {#each orderedSections as [sectionId, section]}
            {#if section?.params?.sectionType && (section?.values || section.params.sectionType === 'text')}
                <div class="relative overflow-x-hidden">
                    <h2 class="text-2xl font-bold text-center mb-2 md:mb-5">
                        {section.title}
                        {#if $isSuperAdmin}
                            <button class="btn btn-square ml-2" on:click={() => setupSection(pageId, sectionId)}>
                                <span class="w-6 h-6"><Edit /></span>
                            </button>
                        {/if}
                    </h2>

                    {#if section?.params?.sectionType === 'text'}
                        <SectionsText {pageId} {sectionId} />
                    {:else if section?.params?.sectionType === 'stalls'}
                        <SectionsStalls {pageId} {sectionId} />
                    {:else if section?.params?.sectionType === 'products'}
                        <SectionsProducts {pageId} {sectionId} />
                    {:else if section?.params?.sectionType === 'products_with_slider'}
                        <SectionsProductsSlider {pageId} {sectionId} {setupSection} />
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
    <ProductCardBrowser {maxProductsLoaded} />
{/if}
