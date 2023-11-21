<script lang="ts">
    import {getPageContent, pageBuilderWidgetType, saveSectionSetup} from "$lib/pagebuilder";
    import {NostrGlobalConfig} from "$sharedLib/stores";

    let pageId;
    let sectionId;

    let page = null;

    let sectionType;
    let maxProductsShown;
    let saved;
    let sectionTitle;

    export function setSection(pageIdLoad, sectionIdLoad) {
        // Clear
        saved = false;

        // Set
        pageId = pageIdLoad;
        sectionId = sectionIdLoad;

        page = getPageContent(pageId, $NostrGlobalConfig);

        sectionTitle        = page?.sections[sectionId]?.title ?? '';
        sectionType         = page?.sections[sectionId]?.params?.sectionType ?? null;
        maxProductsShown    = page?.sections[sectionId]?.params?.maxProductsShown ?? 0;

        window.setup_section.showModal();
    }

    function save() {
        saveSectionSetup(pageId, sectionId, {
            sectionTitle,
            sectionType,
            maxProductsShown
        });

        saved = true;
        console.log('SAVED!!!!!!!!!');
    }
</script>

<dialog id="setup_section" class="modal">
    <div class="modal-box">
        {#if page}
            {#if !saved}
                <p class="text-lg">
                    {#if page.title && page.sections[sectionId]}
                        Editing section <b><i>{page.sections[sectionId].title}</i></b> in page <b><i>{page.title}</i></b>:
                    {:else}
                        Editing section {sectionId} from page {pageId}
                    {/if}
                </p>

                <div class="mt-6">
                    Section title:
                    <input type="text" placeholder="section title" class="mt-2 input input-bordered input-sm w-full max-w-xs" bind:value={sectionTitle} />
                </div>

                {#if !sectionType}
                    <p class="pt-8">Choose a widget type to configure the section.</p>
                {/if}

                <select bind:value={sectionType} class="mt-6 select select-bordered zzzzz-w-full zzzzz-max-w-xs">
                    <option></option>

                    {#each Object.entries(pageBuilderWidgetType) as [widget_id, widget]}
                        <option value={widget_id}>{widget.title}</option>
                    {/each}
                </select>

                {#if sectionType}
                    <div class="mt-6">
                        Description:
                        <p class="mt-2">{pageBuilderWidgetType[sectionType].description}</p>
                    </div>

                    {#if pageBuilderWidgetType[sectionType].max_num_available}
                        <div class="mt-6">
                            Max number of products shown in the section:
                            <input type="text" placeholder="max products shown" class="mt-2 input input-bordered input-sm w-full max-w-xs" bind:value={maxProductsShown} />
                        </div>
                    {/if}
                {/if}
            {:else}
                {#if pageBuilderWidgetType[sectionType].items}
                    <div class="mt-6">
                        <p class="mb-2">Configuration saved. Now you can add content to the section from one of this places:</p>

                        {#if pageBuilderWidgetType[sectionType].items.includes('stalls')}
                            <a class="btn btn-sm btn-primary btn-outline mr-2" target="_blank" href="/stalls">Stall Browser</a>
                        {/if}
                        {#if pageBuilderWidgetType[sectionType].items.includes('products')}
                            <a class="btn btn-sm btn-primary btn-outline mr-2" target="_blank" href="/planet">Planet</a>
                            <a class="btn btn-sm btn-primary btn-outline mr-2" target="_blank" href="/">Homepage</a>
                            <a class="btn btn-sm btn-primary btn-outline mr-2 btn-disabled">Any stall</a>
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
