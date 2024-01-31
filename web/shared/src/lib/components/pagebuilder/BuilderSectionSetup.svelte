<script lang="ts">
    import {browser} from "$app/environment";
    import {fileConfiguration, NostrGlobalConfig} from "$sharedLib/stores";
    import {getConfigurationKey, subscribeConfiguration} from "$sharedLib/services/nostr";
    import {getPage, pageBuilderWidgetType, saveSectionSetup} from "$sharedLib/pagebuilder";
    import RichTextComposer from "$sharedLib/components/pagebuilder/lexical-editor/RichTextComposer.svelte";

    let pageId;
    let sectionId;

    let page = null;

    let sectionType;
    let maxProductsShown;
    let sectionTitle;

    let getLexicalContent;
    let initialMinifiedLexicalContent = '';
    let lastProductPassed = null;

    let closeWhenSaved = false;

    $: saved = false;

    $: if (saved && closeWhenSaved) {
        window.setup_section.close();
    }
    export async function setupSection(pageIdLoad, sectionIdLoad, product = null, closeModalWhenSaved = false) {
        // Clear
        saved = false;

        // Set
        closeWhenSaved = closeModalWhenSaved;

        pageId = pageIdLoad;
        sectionId = sectionIdLoad;

        page = getPage(pageId, $NostrGlobalConfig);

        sectionTitle = page?.sections[sectionId]?.title ?? '';
        sectionType = page?.sections[sectionId]?.params?.sectionType ?? null;
        maxProductsShown = page?.sections[sectionId]?.params?.maxProductsShown ?? 0;

        if (sectionType === 'text') {
            if ($fileConfiguration && $fileConfiguration.admin_pubkeys.length > 0) {
                let receivedAt = 0;

                initialMinifiedLexicalContent = '';

                subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('sectionText_' + pageId + '_' + sectionId)],
                    (initialMinifiedLexicalContentFromNostr, rcAt) => {
                        if (rcAt > receivedAt) {
                            receivedAt = rcAt;
                            initialMinifiedLexicalContent = initialMinifiedLexicalContentFromNostr;
                        }
                    });
            }
        }

        if (sectionType === 'products_with_slider') {
            if (product) {
                if ($fileConfiguration && $fileConfiguration.admin_pubkeys.length > 0) {
                    lastProductPassed = product;

                    let receivedAt = 0;

                    initialMinifiedLexicalContent = (product.name ?? '') + ('\n\n' + product.description ?? '');

                    subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('section_products_with_slider_' + pageId + '_' + sectionId + '_' + product.id)],
                        (initialMinifiedLexicalContentFromNostr, rcAt) => {
                            if (rcAt > receivedAt) {
                                receivedAt = rcAt;
                                initialMinifiedLexicalContent = initialMinifiedLexicalContentFromNostr;
                            }
                        });
                }
            } else {
                lastProductPassed = null;
            }
        }

        window.setup_section.showModal();
    }

    function save() {
        let lexicalContent = null;

        if (sectionType === 'text' || (sectionType === 'products_with_slider' && lastProductPassed)) {
            lexicalContent = getLexicalContent();
        }

        saveSectionSetup(pageId, sectionId, {
            sectionTitle,
            sectionType,
            maxProductsShown,
            lexicalContent,
            lastProductPassed
        });

        saved = true;
    }
</script>

<dialog id="setup_section" class="modal">
    <div class="modal-box w-11/12 max-w-5xl">
        {#if page}
            {#if !saved}
                <p class="text-lg">
                    {#if page.title && page.sections[sectionId]}
                        Editing section <b><i>{page.sections[sectionId].title}</i></b> in page <b><i>{page.title}</i></b>:
                    {:else}
                        Editing section {sectionId} from page {pageId}
                    {/if}
                </p>
                {#if sectionType !== 'products_with_slider' || (sectionType === 'products_with_slider' && !lastProductPassed)}
                    <div class="mt-8 mb-8">
                        Section title:
                        <input type="text" class="ml-2 input input-bordered input-sm w-full max-w-xs" bind:value={sectionTitle} />
                    </div>

                    {#if !sectionType}
                        <p class="mb-4">Choose a widget type to configure the section.</p>
                    {/if}

                    <div>
                        Section type:
                        <select bind:value={sectionType} class="ml-2 select select-sm select-bordered">
                            <option></option>

                            {#each Object.entries(pageBuilderWidgetType) as [widget_id, widget]}
                                <option value={widget_id}>{widget.title}</option>
                            {/each}
                        </select>
                    </div>
                {/if}

                {#if sectionType}
                    {#if sectionType !== 'products_with_slider' || (sectionType === 'products_with_slider' && !lastProductPassed)}
                        <div class="mt-2 text-sm">
                            <p>{pageBuilderWidgetType[sectionType].description}</p>
                        </div>
                    {/if}

                    {#if pageBuilderWidgetType[sectionType].max_num_available}
                        <div class="mt-8">
                            Max number of products shown in the section:
                            <input type="text" placeholder="max products shown" class="mt-2 input input-bordered input-sm w-full max-w-xs" bind:value={maxProductsShown} />
                        </div>
                    {/if}

                    {#if browser && initialMinifiedLexicalContent && sectionType === 'text' || (sectionType === 'products_with_slider' && lastProductPassed)}
                        <div class="mt-8">
                            {#key initialMinifiedLexicalContent}
                                <RichTextComposer {initialMinifiedLexicalContent} bind:getLexicalContent={getLexicalContent} />
                            {/key}
                        </div>
                        {#if sectionType === 'products_with_slider'}
                            <span class="mt-8 text-sm">Note: you're not editing the product description. This text will be used only when displaying this product in this section.</span>
                        {/if}
                    {/if}
                {/if}

            {:else}
                {#if pageBuilderWidgetType[sectionType].items}
                    <div class="mt-6">
                        <div class="alert alert-info mb-4">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 size-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            <span>Configuration saved. Now you can add content to the section from any of this places:</span>
                        </div>

                        {#if pageBuilderWidgetType[sectionType].items.includes('stalls')}
                            <a class="btn btn-sm btn-primary btn-outline mr-2" target="_blank" href="/stalls">Stall Browser</a>
                        {/if}
                        {#if pageBuilderWidgetType[sectionType].items.includes('products')}
                            <a class="btn btn-sm btn-primary btn-outline mr-2" target="_blank" href="/planet">Planet</a>
                            <a class="btn btn-sm btn-primary btn-outline mr-2" target="_blank" href="/">Homepage</a>
                            <a class="btn btn-sm btn-primary btn-outline mr-2 btn-disabled" href={null}>Any stall</a>
                        {/if}
                    </div>
                {:else}
                    <div class="flex">
                        <p class="mx-auto mt-8 mb-4">Changes saved</p>
                    </div>
                {/if}
            {/if}
        {/if}

        <div class="modal-action">
            <form method="dialog">
                {#if page && !saved}
                    <button class="btn btn-success mr-3" class:btn-disabled={!sectionType || !sectionTitle} on:click|preventDefault={save}>Save</button>
                {/if}
                <button class="btn">Close</button>
            </form>
        </div>
    </div>
</dialog>
