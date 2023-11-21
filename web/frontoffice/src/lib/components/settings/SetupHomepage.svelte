<script lang="ts">
    import {onMount} from 'svelte';
    import {NostrPublicKey, NostrGlobalConfig} from "$sharedLib/stores";
    import {getConfigurationFromFile, requestLoginModal} from "$sharedLib/utils";
    import Trash from "$sharedLib/components/icons/Trash.svelte";
    import Edit from "$sharedLib/components/icons/Edit.svelte";
    import { SortableList } from '@jhubbardsf/svelte-sortablejs'
    import {
        initializeContentForGlobalConfig,
        addSectionToPage,
        removeSection,
        handleEnd,
        getPage,
        pageBuilderWidgetType
    } from "$lib/pagebuilder";
    import BuilderSectionSetup from "$lib/components/pagebuilder/BuilderSectionSetup.svelte";

    let isSuperAdmin: boolean = false;
    let newSection = '';
    let content = null;
    let orderedSections;

    const pageId = 0;

    $: { content = getPage(pageId, $NostrGlobalConfig); }

    $: if (content && content.sections) {
        orderedSections = Object.entries(content.sections).sort((a, b) => {
            return a[1].order - b[1].order;
        });
    }

    $: console.log('orderedSections', orderedSections);

    let setupSection;

    onMount(async () => {
        let config = await getConfigurationFromFile();
        if (config && config.admin_pubkeys.includes($NostrPublicKey)) {
            isSuperAdmin = true;
            initializeContentForGlobalConfig($NostrGlobalConfig);
        }
    });
</script>

<div class="w-full items-center justify-center text-center">
    {#if $NostrPublicKey}
        {#if isSuperAdmin}
            <div id="simple-list" class="mt-4 border rounded p-6">
                <h2 class="font-bold">Homepage Sections</h2>

                <div class="my-8">
                    Add sections to the homepage and set them up to display what you need to show in each section.
                </div>

                <div class="w-6/12 mx-auto">
                    <div class="mt-10 mb-4">
                        <input type="text" bind:value={newSection} placeholder="Title of new section" class="input input-bordered input-success w-full max-w-xs input-sm" />
                        <button class="btn btn-sm btn-success ml-1" on:click={() => {let newSectionId = addSectionToPage(newSection); setupSection(pageId, newSectionId); newSection=''}}>Add</button>
                    </div>

                    {#if content && content.sections}
                        <SortableList
                            class="list-group col"
                            animation={150}
                            ghostClass="bg-info"
                            onEnd={(evt) => {handleEnd(pageId, evt)}}
                        >
                            {#each orderedSections as [section_id, section]}
                                <div class="grid grid-cols-3 gap-0">
                                    <div class="w-full p-3 text-slate-500 dark:text-slate-400 border border-slate-400 dark:border-slate-500 cursor-move right-0">
                                        {section.title}
                                    </div>
                                    <div class="w-full p-3 text-slate-500 dark:text-slate-400 border border-slate-400 dark:border-slate-500 cursor-move right-0">
                                        {#if section?.params?.sectionType}
                                            {pageBuilderWidgetType[section.params.sectionType].title}
                                        {:else}
                                            -
                                        {/if}
                                    </div>
                                    <div class="w-full p-3 text-slate-500 dark:text-slate-400 border border-slate-400 dark:border-slate-500 align-middle">
                                        <div class="tooltip" data-tip="Edit section">
                                            <button class="btn btn-xs btn-info btn-outline" on:click={() => setupSection(pageId, section_id)}><span class="w-5"><Edit /></span></button>
                                        </div>
                                        <div class="tooltip" data-tip="Remove section">
                                            <button class="btn btn-xs btn-error btn-outline ml-1" on:click={() => removeSection(pageId, section_id)}><span class="w-5"><Trash /></span></button>
                                        </div>
                                    </div>
                                </div>
                            {/each}
                        </SortableList>

                        <div class="text-slate-600 dark:text-slate-300 pt-2 text-xs">
                            You can reorder this sections by dragging them up and down
                        </div>

                        {#each orderedSections as [section_id, section]}
                            <p>{section.title}</p>
                        {/each}
                    {:else}
                        <div class="list-group-item">
                            Homepage Section
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
