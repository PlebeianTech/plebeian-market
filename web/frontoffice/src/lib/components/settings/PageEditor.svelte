<script lang="ts">
    import {NostrPublicKey, NostrGlobalConfig, isSuperAdmin} from "$sharedLib/stores";
    import {requestLoginModal} from "$sharedLib/utils";
    import Trash from "$sharedLib/components/icons/Trash.svelte";
    import Edit from "$sharedLib/components/icons/Edit.svelte";
    import DragBars from "$sharedLib/components/icons/DragBars.svelte";
    import { SortableList } from '@jhubbardsf/svelte-sortablejs'
    import {
        addSectionToPage,
        removeSection,
        handleMove,
        getPage,
        pageBuilderWidgetType,
        getPages,
        removePage,
        savePageParams, addPage
    } from "$sharedLib/pagebuilder";
    import BuilderSectionSetup from "$sharedLib/components/pagebuilder/BuilderSectionSetup.svelte";
    import AlertInfo from "$sharedLib/components/icons/AlertInfo.svelte";
    import ArrowLeft from "$sharedLib/components/icons/ArrowLeft.svelte";

    // Pages
    let newPageTitle = '';
    let pageTitle = '';
    let pageSlug = '';

    // Sections
    let newSection = '';
    let content = null;
    let orderedSections = null;


    let selectedPageId: string | null = null;

    function setParamsEditPage() {
        content = getPage(selectedPageId, $NostrGlobalConfig);

        pageTitle = content?.title ?? '';
        pageSlug = content?.slug ?? '';
    }

    $: if (content) {
        if (content.sections) {
            orderedSections = Object.entries(content.sections).sort((a, b) => {
                return a[1].order - b[1].order;
            });
        } else {
            orderedSections = null;
        }
    }

    let setupSection;
</script>

<div class="w-full items-center justify-center text-center">
    {#if $NostrPublicKey}
        {#if $isSuperAdmin}
            {#if !selectedPageId}
                <div class="mt-10 mb-4">
                    <input type="text" bind:value={newPageTitle} placeholder="Title of the new page" class="input input-bordered input-success w-full max-w-xs input-sm" />
                    <button class="btn btn-sm btn-success ml-1" class:btn-disabled={!newPageTitle}
                            on:click={() => {selectedPageId = addPage(newPageTitle); setParamsEditPage(); newPageTitle=''}}>
                        Add
                    </button>
                </div>

                <h2 class="font-bold">Pages</h2>
                <div class="2xl:w-11/12 3xl:w-9/12 mx-auto text-xs aaamd:text-base mt-4 mb-16">
                    <table class="table min-w-full">
                        <thead>
                            <tr>
                                <th class="py-2 px-4 bg-gray-100 dark:bg-gray-700 text-center">Page Title</th>
                                <th class="py-2 px-4 bg-gray-100 dark:bg-gray-700 text-center">Slug</th>
                                <th class="py-2 px-4 bg-gray-100 dark:bg-gray-700 text-center"># Sections</th>
                                <th class="py-2 px-4 bg-gray-100 dark:bg-gray-700 text-center">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each Object.entries(getPages($NostrGlobalConfig)) as [pageId, page]}
                                <tr>
                                    <td class="py-2 px-4 text-center">{page.title}</td>
                                    <td class="py-2 px-4 text-center">
                                        {#if pageId === '0'}
                                            /
                                        {:else if !page.slug}
                                            <div class="flex relative mx-auto w-fit">
                                                <span class="text-red-500 text-xs font-bold inline-block align-text-bottom">Slug needed</span>
                                                <div class="ml-2 tooltip" data-tip="A slug is needed so this page works correctly">
                                                    <AlertInfo />
                                                </div>
                                            </div>
                                        {:else}
                                            /{page.slug}
                                        {/if}
                                    </td>
                                    <td class="py-2 px-4 text-center">
                                        {#if page.sections}
                                            {Object.keys(page.sections).length}
                                        {/if}
                                    </td>
                                    <td class="py-2 px-4 text-center">
                                        <div class="tooltip" data-tip="Edit page">
                                            <button class="btn btn-xs md:btn-sm btn-info btn-outline" on:click={() => {selectedPageId = pageId; setParamsEditPage()}}><span class="w-5"><Edit /></span></button>
                                        </div>
                                        <div class="tooltip" data-tip="Remove page">
                                            <button class="btn btn-xs md:btn-sm btn-error btn-outline mt-2 md:mt-0 md:ml-2" on:click={() => removePage(pageId)}><span class="w-5"><Trash /></span></button>
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {/if}

            {#if selectedPageId}
                <div class="flex items-start justify-start text-left align-middle ml-4 lg:ml-14 2xl:ml-28 3xl:ml-32">
                    <div class="w-10 mr-2 cursor-pointer" on:click={() => selectedPageId = null}>
                        <ArrowLeft />
                    </div>
                    <div class="w-10 cursor-pointer" on:click={() => selectedPageId = null}>
                        <span class="inline-block align-middle text-lg mt-1">Back</span>
                    </div>
                </div>
                <h2>Editing <span class="font-bold">{getPage(selectedPageId, $NostrGlobalConfig).title}</span> page content.</h2>

                {#if selectedPageId && selectedPageId !== '0'}
                    <div class="2xl:w-11/12 3xl:w-9/12 mx-auto text-xs md:text-base">
                        <div class="my-4 grid">
                            <div class="mb-4">Page Title: <input type="text" bind:value={pageTitle} placeholder="Title of the new page" class="input input-success w-full max-w-xs input-sm {!pageTitle ? 'input-error border-2' : 'input-bordered'}" /></div>

                            <div class="mb-4">
                                Page Slug: <input type="text" bind:value={pageSlug} placeholder="something meaningful like: /about" class="input input-bordered input-success w-full max-w-xs input-sm {!pageSlug ? 'input-error border-2' : 'input-bordered'}" />
                                <div class="mt-2 tooltip" data-tip="The slug is the part of the URL that will point to this page. If your site is mysite.com, and the slug is /mypage, this page will be available at mysite.com/mypage">
                                    <AlertInfo />
                                </div>
                            </div>

                            <div class="mb-4">
                                <button class="btn btn-sm btn-success ml-1"
                                        on:click={() => {savePageParams(selectedPageId, pageTitle, pageSlug)}}>
                                    Save
                                </button>
                            </div>
                        </div>
                    </div>
                {/if}

                <div class="mt-12">
                    <p>Add sections here, and set them up to display what you need to show in each of them.</p>
                </div>

                <div class="mt-5 mx-auto text-xs md:text-base">
                    <div class="mb-4">
                        <input type="text" bind:value={newSection} placeholder="Title of the new section" class="input input-bordered input-success w-full max-w-xs input-sm" />
                        <button class="btn btn-sm btn-success ml-1" class:btn-disabled={!newSection}
                                on:click={() => {let newSectionId = addSectionToPage(newSection, selectedPageId); setupSection(selectedPageId, newSectionId); newSection=''}}>
                            Add
                        </button>
                    </div>

                    {#if orderedSections && orderedSections.length > 0}
                        {#key orderedSections}
                            <div class="grid grid-cols-5 gap-0 align-middle">
                                <div class="w-full p-3 border border-slate-400 dark:border-slate-500 right-0 font-bold flex items-center justify-center"></div>
                                <div class="w-full p-3 border border-slate-400 dark:border-slate-500 right-0 font-bold flex items-center justify-center">Section Title</div>
                                <div class="w-full p-3 border border-slate-400 dark:border-slate-500 right-0 font-bold flex items-center justify-center">Section Type</div>
                                <div class="w-full p-3 border border-slate-400 dark:border-slate-500 right-0 font-bold flex items-center justify-center"># elements</div>
                                <div class="w-full p-3 border border-slate-400 dark:border-slate-500 font-bold flex items-center justify-center">Actions</div>
                            </div>

                            <SortableList
                                class="list-group col"
                                animation={150}
                                ghostClass="bg-info"
                                onEnd={(evt) => {handleMove(selectedPageId, evt)}}
                            >
                                {#each orderedSections as [sectionId, section]}
                                    <div class="grid grid-cols-5 gap-0 align-middle">
                                        <div class="w-full p-3 border border-slate-400 dark:border-slate-500 cursor-move right-0 flex items-center justify-center">
                                            <div class="w-8 mx-auto tooltip" data-tip="Change section ordering dragging up or down">
                                                <DragBars />
                                            </div>
                                        </div>
                                        <div class="w-full p-3 border border-slate-400 dark:border-slate-500 cursor-move right-0 flex items-center justify-center">
                                            {section.title}
                                        </div>
                                        <div class="w-full p-3 border border-slate-400 dark:border-slate-500 cursor-move right-0 flex items-center justify-center">
                                            {#if section?.params?.sectionType}
                                                {pageBuilderWidgetType[section.params.sectionType].title}
                                            {:else}
                                                -
                                            {/if}
                                        </div>
                                        <div class="w-full p-3 border border-slate-400 dark:border-slate-500 cursor-move right-0 flex items-center justify-center">
                                            {#if section?.values && section.values[section.params.sectionType]}
                                                {section.values[section.params.sectionType].length} {pageBuilderWidgetType[section.params.sectionType].items[0] ?? ''}
                                            {:else}
                                                {#if section?.params?.sectionType === 'text'}
                                                    -
                                                {:else if section?.params?.sectionType === 'products_with_slider' && section?.values}
                                                    {section.values['products'].length} {pageBuilderWidgetType[section.params.sectionType].items[0] ?? ''}
                                                {:else}
                                                    0
                                                {/if}
                                            {/if}
                                        </div>
                                        <div class="w-full p-3 border border-slate-400 dark:border-slate-500 block md:flex items-center justify-center">
                                            <div class="tooltip" data-tip="Edit section">
                                                <button class="btn btn-xs md:btn-sm btn-info btn-outline" on:click={() => setupSection(selectedPageId, sectionId)}><span class="w-5"><Edit /></span></button>
                                            </div>
                                            <div class="tooltip" data-tip="Remove section">
                                                <button class="btn btn-xs md:btn-sm btn-error btn-outline mt-2 md:mt-0 md:ml-2" on:click={() => removeSection(selectedPageId, sectionId)}><span class="w-5"><Trash /></span></button>
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                            </SortableList>
                        {/key}

                        <div class="pt-2 text-xs">
                            You can reorder this sections by dragging them up and down
                        </div>
                    {/if}
                </div>
            {/if}

        {:else}
            <p>You need to be the owner of this website to be able to customize its default appearance.</p>
            <p class="mt-6">To claim ownership, you need to <b>edit the file <code>config.json</code></b> and put there your <b>Nostr public key</b>: {$NostrPublicKey} </p>
            <p class="mt-6">You'll then be able to come to this page and customize your installation of Plebeian Market.</p>
        {/if}
    {:else}
        <p>You need to be the owner of this website and login using your Nostr account:</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    {/if}
</div>

<BuilderSectionSetup bind:setupSection={setupSection} />
