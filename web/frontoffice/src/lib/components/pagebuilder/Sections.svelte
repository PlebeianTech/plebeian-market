<script lang="ts">
    import {NostrGlobalConfig} from "$sharedLib/stores";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    import {getPageContent} from "$lib/pagebuilder";

    export let page;

    const maxProductsLoaded = 20;

    let content = null;
    let orderedSections;

    $: { content = getPageContent(page, $NostrGlobalConfig); }

    $: if (content && content.sections) {
        orderedSections = Object.entries(content.sections).sort((a, b) => {
            return a[1].order - b[1].order;
        });
    }

    $: console.log('orderedSections', orderedSections);
</script>

{#if content && content.sections}
    {#each orderedSections as [section_id, section]}
        <!-- {(console.log('Sections.svelte - section', section), '')} -->

        {#if section?.params?.sectionType}
            <h1>{section.title}</h1>

            {#if section?.params?.sectionType === 'stalls'}
                ----- Stalls
            {:else if section?.params?.sectionType === 'products'}
                ----- Products
            {:else if section?.params?.sectionType === 'stall_products'}
                ----- Stall Products
            {/if}
        {/if}
    {/each}
{:else}
    <ProductCardBrowser whiteListedStalls={$NostrGlobalConfig.homepage_include_stalls} {maxProductsLoaded} />
{/if}