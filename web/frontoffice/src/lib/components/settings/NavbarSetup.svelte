<script lang="ts">
    import {onMount} from "svelte";
    import {getAppRoutes, getPages, pagesEnabledByDefault, pagesAndTitles} from "$sharedLib/pagebuilder";
    import {flip} from "svelte/animate";
    import {dndzone} from "svelte-dnd-action";
    import {fileConfiguration, Info} from "$sharedLib/stores";
    import {getConfigurationKey, publishConfiguration, subscribeConfiguration} from "$sharedLib/services/nostr";
    import DragBars from "$sharedLib/components/icons/DragBars.svelte";

    let allPagesList = [];
    let allPagesListCurrentStatus = [];
    let allPagesListReceivedAt = 0;
    let nostrConfigFinishedLoading = false;
    let configFromNostr = false;

    let appPages;
    let virtualPages;

    let currentlyDragging = false;
    const flipDurationMs = 200;

    function handleDndConsider(e) {
        currentlyDragging = true;
        allPagesList = e.detail.items;
    }
    function handleDndFinalize(e) {
        currentlyDragging = false;
        allPagesList = e.detail.items;
    }

    function saveToNostr() {
        publishConfiguration(allPagesList, getConfigurationKey('header_config'),
            () => {
                allPagesListCurrentStatus = JSON.stringify(allPagesList);
            });

        Info.set('Changes saved!')
    }

    function pageAlreadyExists(p_id: string): boolean {
        for (const page of allPagesList) {
            if (page.p_id === p_id) return true;
        }

        return false;
    }

    function buildAllPagesList(onlyAddNewOnes: boolean = false) {
        appPages = getAppRoutes();
        virtualPages = getPages();

        let i = 0;

        if (onlyAddNewOnes) {
            for (const page of allPagesList) {
                if (page.id > i) {
                    i = page.id;
                }
            }

            i++;
        }

        if (virtualPages) {
            for (const [id, virtualPage] of Object.entries(virtualPages)) {
                if (
                    (!onlyAddNewOnes && allPagesListReceivedAt === 0)
                    ||
                    (onlyAddNewOnes && !pageAlreadyExists('virt-'+id))
                ) {
                    allPagesList.push({
                        id: i,
                        p_id: 'virt-'+id, // virtualPage.title,
                        enabled: false
                    });
                    i++;
                }
            }
        }

        if (appPages) {
            for (const appPage of appPages) {
                if (
                    (!onlyAddNewOnes && allPagesListReceivedAt === 0)
                    ||
                    (onlyAddNewOnes && !pageAlreadyExists(appPage))
                ) {
                    allPagesList.push({
                        id: i,
                        p_id: appPage,
                        enabled: pagesEnabledByDefault.includes(appPage)
                    });
                    i++;
                }
            }
        }

        if (onlyAddNewOnes) {
            allPagesListCurrentStatus = JSON.stringify(allPagesList);
        }

        if (allPagesListReceivedAt === 0) {
            allPagesList = allPagesList;    // fire reactivity
        }
    }

    $: if (!currentlyDragging && nostrConfigFinishedLoading && (!configFromNostr || (configFromNostr && allPagesListCurrentStatus !== JSON.stringify(allPagesList))) && allPagesList.length > 0) {
        saveToNostr();
    }

    onMount(async () => {
        // Try to load the list from Nostr
        if ($fileConfiguration && $fileConfiguration.admin_pubkeys.length > 0) {
            subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('header_config')],
                (navbarConfigFromNostr, rcAt) => {
                    if (rcAt > allPagesListReceivedAt) {
                        if (navbarConfigFromNostr.length > 0) {
                            configFromNostr = true;
                            allPagesListReceivedAt = rcAt;
                            allPagesList = navbarConfigFromNostr;
                            allPagesListCurrentStatus = JSON.stringify(navbarConfigFromNostr);

                            buildAllPagesList(true);
                        }
                    }
                },
                () => {
                    nostrConfigFinishedLoading = true;
                });
        }

        // But start building the list of pages, just in case it was never saved
        buildAllPagesList();
    });
</script>

<div>
    <p>Configure what items appear on the <b>Navigation Bar</b> and the order of those items.</p>
    <p class="mt-6">The navigation bar is shown only while viewing the website in desktop computers. To configure what appears on the menu that is also shown in mobile devices, you can click <a class="underline" href={null}>here</a>.</p>
    <p class="mt-6">- To enable or disable showing an element on the navigation bar, <b>click the "Visible" checkbox</b>.</p>
    <p>- To change the order in which links appear on the Navigation Bar, <b>drag and drop to reorder</b> the items on the list.</p>
</div>

{#if nostrConfigFinishedLoading && allPagesList && allPagesList.length > 0}
    <div class="grid grid-cols-4 bg-base-300 dark:border dark:border-gray-600 rounded mt-10 p-4 mb-4 font-bold">
        <div></div>
        <div>Title</div>
        <div>Slug</div>
        <div>Visible</div>
    </div>

    <section use:dndzone="{{items: allPagesList, flipDurationMs}}" on:consider="{handleDndConsider}" on:finalize="{handleDndFinalize}">
        {#each allPagesList as page(page.id)}
            <div class="grid grid-cols-4 bg-base-300 dark:border dark:border-gray-600 rounded p-4 mb-2 items-center" animate:flip="{{duration: flipDurationMs}}">
                <div class="w-full cursor-move right-0 flex items-center justify-center">
                    <div class="w-8 mx-auto tooltip" data-tip="Change page ordering dragging up or down">
                        <DragBars />
                    </div>
                </div>
                {#if page.p_id.startsWith('virt-')}
                    <!-- Virtual page -->
                    <div>{virtualPages[page.p_id.substring(5)]?.title ?? ''}</div>
                    <div>/{virtualPages[page.p_id.substring(5)]?.slug ?? ''}</div>
                {:else}
                    <!-- Real page -->
                    <div>{pagesAndTitles[page.p_id]?.title ?? ''}</div>
                    <div>/{page.p_id}</div>
                {/if}
                <div>
                    <input type="checkbox" class="checkbox checkbox-primary" bind:checked={page.enabled} />
                </div>
            </div>
        {/each}
    </section>
{:else}
    <div class="p-12 flex flex-wrap items-center justify-center">
        <span class="loading loading-bars w-64"></span>
    </div>
{/if}