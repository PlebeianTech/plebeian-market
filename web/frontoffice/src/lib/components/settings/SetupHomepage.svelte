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
        pageBuilderWidgetType
    } from "$lib/pagebuilder";
    import BuilderSectionSetup from "$lib/components/pagebuilder/BuilderSectionSetup.svelte";

    let newSection = '';
    let content = null;
    let orderedSections = null;

    const pageId = 0;

    $: { content = getPage(pageId, $NostrGlobalConfig); }

    $: if (content && content.sections) {
        orderedSections = Object.entries(content.sections).sort((a, b) => {
            return a[1].order - b[1].order;
        });
    }

    let setupSection;

    $: {
        console.log('SetupHomepage(js) - $NostrPublicKey: ', $NostrPublicKey);
        console.log('SetupHomepage(js) - $isSuperAdmin: ', $isSuperAdmin);
    }
</script>

<div class="w-full items-center justify-center text-center">
    {(console.log('SetupHomepage(html) - $NostrPublicKey', $NostrPublicKey), '')}
    {(console.log('SetupHomepage(html) - $isSuperAdmin', $isSuperAdmin), '')}
    {#if $NostrPublicKey}
        {#if $isSuperAdmin}
            <div id="simple-list" class="mt-4 border rounded p-2 md:p-6">
                <h2 class="font-bold">Homepage Sections</h2>

                <div class="my-8">
                    <p>With this functionality, you can customize what is shown on the homepage.</p>
                    <p class="mt-4">Add sections here, and set them up to display what you need to show in each of them.</p>
                </div>

                <div class="md:w-6/12 mx-auto text-xs md:text-base">
                    <div class="mt-10 mb-4">
                        <input type="text" bind:value={newSection} placeholder="Title of new section" class="input input-bordered input-success w-full max-w-xs input-sm" />
                        <button class="btn btn-sm btn-success ml-1"
                                class:btn-disabled={!newSection}
                                on:click={() => {let newSectionId = addSectionToPage(newSection); setupSection(pageId, newSectionId); newSection=''}}>
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
                                onEnd={(evt) => {handleMove(pageId, evt)}}
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
                                                <button class="btn btn-xs md:btn-sm btn-info btn-outline" on:click={() => setupSection(pageId, sectionId)}><span class="w-5"><Edit /></span></button>
                                            </div>
                                            <div class="tooltip" data-tip="Remove section">
                                                <button class="btn btn-xs md:btn-sm btn-error btn-outline mt-2 md:mt-0 md:ml-2" on:click={() => removeSection(pageId, sectionId)}><span class="w-5"><Trash /></span></button>
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
            </div>

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
