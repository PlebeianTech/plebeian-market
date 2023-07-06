<script lang="ts">
    import { onMount } from 'svelte';
    import {NostrGlobalConfig, NostrPublicKey} from "$lib/stores";
    import {getConfigurationFromFile, requestLoginModal} from "$lib/utils";
    import { SortableList } from '@jhubbardsf/svelte-sortablejs'
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import Minus from "$sharedLib/components/icons/Minus.svelte";
    import Trash from "$sharedLib/components/icons/Trash.svelte";
    import Edit from "$sharedLib/components/icons/Edit.svelte";

    // TODO
    let isSuperAdmin: boolean = true;

    let sections = [{id: 1, title: 'Section 1'}, {id: 2, title: 'Section 2'}, {id: 3, title: 'Section 3'}];
    let newSection = '';

    function saveSectionsToNostr() {
        let order = 0;

        sections.forEach(section => {
            section.order = order;
            order++;
        })

        // console.log('data after:', sections);

        $NostrGlobalConfig.homepage_sections = sections;
    }

    function addItem() {
        if (newSection !== '') {
            let sectionIdNewElement = 0;

            sections.forEach(section => {
                if (section.id > sectionIdNewElement) {
                    sectionIdNewElement = section.id;
                }
            })

            sectionIdNewElement++;

            sections = [...sections, {id: sectionIdNewElement, title: newSection}];
            newSection = '';

            saveSectionsToNostr();
        }
    }

    const move = (arr, from, to) => {
        const input = [...arr];
        let numberOfDeletedElm = 1;

        const elm = input.splice(from, numberOfDeletedElm)[0];
        numberOfDeletedElm = 0;
        input.splice(to, numberOfDeletedElm, elm);
        sections = [...input];
    };

    const handleEnd = (evt) => {
        move(sections, evt.oldIndex, evt.newIndex);

        saveSectionsToNostr();
    };

    function removeItem(index) {
        sections = sections.filter((section, _) => section.id !== index);

        saveSectionsToNostr();
    }

    onMount(async () => {
        let config = await getConfigurationFromFile();
        if (config && $NostrPublicKey === config.admin_pubkey) {
            isSuperAdmin = true;
        }

        // TODO REMOVE
        // saveSectionsToNostr();
    });
</script>

<div class="w-full items-center justify-center text-center">
    {#if $NostrPublicKey}
        {#if isSuperAdmin}
            <p>To add stalls to the homepage default view, go to the <a class="btn btn-sm btn-primary btn-outline" href="/stalls">Stall Browser</a>
                and add them or remove them using the <span class="inline-block text-green-500 align-middle"><Plus /></span> and
                <span class="inline-block text-rose-500 align-middle"><Minus /></span> icons at the right.
            </p>
            <p class="mt-8">
                If you want to create more complex layouts, you can add different sections below, and you'll be able to add different products or stalls to each section.
            </p>
<!--
            <div class="divider my-8"></div>

            <div id="simple-list" class="mt-4 border rounded p-6">
                <h2 class="font-bold">Homepage Sections</h2>

                <div class="my-10">
                    Add sections to the homepage, and then you'll be able to add products or stalls to those sections.
                </div>

                <div class="w-6/12 mx-auto">
                    <div class="mt-10 mb-4">
                        <input type="text" bind:value={newSection} placeholder="Title of new section" class="input input-bordered input-success w-full max-w-xs input-sm" />
                        <button class="btn btn-sm btn-success ml-1" on:click={addItem}>Add</button>
                    </div>

                    {#if sections.length > 0}
                        <SortableList
                            class="list-group col"
                            animation={150}
                            ghostClass="bg-info"
                            onEnd={handleEnd}
                        >
                            {#each sections as section (section.id)}
                                <div class="grid grid-cols-2 gap-0">
                                    <div class="w-full p-3 text-slate-500 dark:text-slate-400 border border-slate-400 dark:border-slate-500 cursor-move right-0">
                                        {section.title}
                                    </div>
                                    <div class="w-full p-3 text-slate-500 dark:text-slate-400 border border-slate-400 dark:border-slate-500 align-middle">
                                        <div class="tooltip" data-tip="Edit section">
                                            <button class="btn btn-xs btn-info btn-outline" on:click={() => console.log('Edit index=',section.id)}><span class="w-5"><Edit /></span></button>
                                        </div>
                                        <div class="tooltip" data-tip="Remove section">
                                            <button class="btn btn-xs btn-error btn-outline ml-1" on:click={() => removeItem(section.id)}><span class="w-5"><Trash /></span></button>
                                        </div>
                                    </div>
                                </div>
                            {/each}
                        </SortableList>

                        <div class="text-slate-500 dark:text-slate-400 pt-2 text-xs">
                            You can reorder your sections by dragging them up and down
                        </div>

                    {:else}
                        <div class="list-group-item">
                            Homepage Section
                        </div>
                    {/if}
                </div>
            </div>
-->
        {:else}
            <p>You need to be the owner of this website to be able to customize its default appearance.</p>
            <p class="mt-6">To claim ownership, you need to <b>edit the file <code>config.json</code></b> and put there your <b>Nostr public key</b>: {$NostrPublicKey} </p>
            <p class="mt-6">You'll then be able to come to this page and learn how to customize your installation of Plebeian Market.</p>
        {/if}
    {:else}
        <p>You need to be the owner of this website and login using your Nostr account:</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    {/if}
</div>
