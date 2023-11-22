<script lang="ts">
    import {NostrGlobalConfig, NostrPublicKey} from "$sharedLib/stores";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    import {getPage} from "$lib/pagebuilder";
    import SectionsStalls from "$lib/components/pagebuilder/SectionsStalls.svelte";
    import SectionsProducts from "$lib/components/pagebuilder/SectionsProducts.svelte";
    import {onMount} from "svelte";
    import {getConfigurationFromFile} from "$sharedLib/utils";

    export let pageId;

    const maxProductsLoaded = 20;

    let isSuperAdmin: boolean = false;

    let content = null;
    let orderedSections;

    $: { content = getPage(pageId, $NostrGlobalConfig); }

    $: if (content && content.sections) {
        orderedSections = Object.entries(content.sections).sort((a, b) => {
            return a[1].order - b[1].order;
        });
    }

    onMount(async () => {
        let config = await getConfigurationFromFile();
        if (config && config.admin_pubkeys.includes($NostrPublicKey)) {
            isSuperAdmin = true;
        }
    });
</script>

{#if content && content.sections}
    <div class="pt-12">
        {#each orderedSections as [sectionId, section]}
            {#if section?.params?.sectionType && section?.values}
                <div class="relative overflow-x-hidden">
                    <h2 class="text-2xl font-bold text-center mb-5">{section.title}</h2>

                    {#if section?.params?.sectionType === 'text'}
                        ------ Texto
                    {:else if section?.params?.sectionType === 'stalls'}
                        <SectionsStalls {pageId} {sectionId} {isSuperAdmin} />
                    {:else if section?.params?.sectionType === 'products'}
                        <SectionsProducts {pageId} {sectionId} {isSuperAdmin} />
                    {:else if section?.params?.sectionType === 'stall_products'}
                        ----- Stall Products
                    {/if}
                </div>

                <div class="divider w-[80%] mx-auto my-10"></div>
            {/if}
        {/each}
    </div>
{:else}
    <ProductCardBrowser {maxProductsLoaded} />
{/if}