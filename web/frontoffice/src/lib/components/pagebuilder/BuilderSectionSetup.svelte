<script lang="ts">
    import {getPage, pageBuilderWidgetType, saveSectionSetup} from "$lib/pagebuilder";
    import {NostrGlobalConfig} from "$sharedLib/stores";
    import { useProsemirrorAdapterProvider } from "@prosemirror-adapter/svelte";
    import Editor from "$lib/components/pagebuilder/editor/Editor.svelte";
    import {getConfigurationFromFile} from "$sharedLib/utils";
    import {getConfigurationKey, subscribeConfiguration} from "$sharedLib/services/nostr";

    useProsemirrorAdapterProvider();

    let pageId;
    let sectionId;

    let page = null;

    let sectionType;
    let maxProductsShown;
    let saved;
    let sectionTitle;

    let getMarkdownContent;
    let initialMarkdownText = '';

    export async function setupSection(pageIdLoad, sectionIdLoad) {
        // Clear
        saved = false;

        // Set
        pageId = pageIdLoad;
        sectionId = sectionIdLoad;

        page = getPage(pageId, $NostrGlobalConfig);

        sectionTitle = page?.sections[sectionId]?.title ?? '';
        sectionType = page?.sections[sectionId]?.params?.sectionType ?? null;
        maxProductsShown = page?.sections[sectionId]?.params?.maxProductsShown ?? 0;


        if (sectionType === 'text') {
            let config = await getConfigurationFromFile();

            if (config && config.admin_pubkeys.length > 0) {
                let receivedAt = 0;

                subscribeConfiguration(config.admin_pubkeys, getConfigurationKey('sectionText' + '_' + pageId + '_' + sectionId),
                    (markdownTextForSection, rcAt) => {
                        if (rcAt > receivedAt) {
                            receivedAt = rcAt;
                            initialMarkdownText = markdownTextForSection;
                        }
                    });
            }
        }

        window.setup_section.showModal();
    }

    function save() {
        let markDownContent = null;

        if (sectionType === 'text') {
            markDownContent = getMarkdownContent();
        }

        saveSectionSetup(pageId, sectionId, {
            sectionTitle,
            sectionType,
            maxProductsShown,
            markDownContent
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

                <div class="mt-8 mb-8">
                    Section title:
                    <input type="text" class="ml-2 input input-bordered input-sm w-full max-w-xs" bind:value={sectionTitle} />
                </div>

                {#if !sectionType}
                    <p class="mb-4">Choose a widget type to configure the section.</p>
                {/if}

                <div>
                    Section type:
                    <select bind:value={sectionType} class="ml-2 select select-sm select-bordered zzzzz-w-full zzzzz-max-w-xs">
                        <option></option>

                        {#each Object.entries(pageBuilderWidgetType) as [widget_id, widget]}
                            <option value={widget_id}>{widget.title}</option>
                        {/each}
                    </select>
                </div>

                {#if sectionType}
                    <div class="mt-2 text-sm">
                        <p>{pageBuilderWidgetType[sectionType].description}</p>
                    </div>

                    {#if pageBuilderWidgetType[sectionType].max_num_available}
                        <div class="mt-8">
                            Max number of products shown in the section:
                            <input type="text" placeholder="max products shown" class="mt-2 input input-bordered input-sm w-full max-w-xs" bind:value={maxProductsShown} />
                        </div>
                    {/if}

                    {#if pageBuilderWidgetType[sectionType].long_text}
                        <div style="display: none">
                            <textarea id="content" bind:value={initialMarkdownText} />
                        </div>

                        <div class="mt-8">
                            <Editor bind:getMarkdownContent={getMarkdownContent} />
                        </div>
                    {/if}
                {/if}

            {:else}
                {#if pageBuilderWidgetType[sectionType].items}
                    <div class="mt-6">
                        <div class="alert alert-info mb-4">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
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
                    <button class="btn btn-success" class:btn-disabled={!sectionType || !sectionTitle} on:click|preventDefault={save}>Save</button>
                {/if}
                <button class="btn">Close</button>
            </form>
        </div>
    </div>
</dialog>
