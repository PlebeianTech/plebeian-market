<script lang="ts">
    import {
        addItemToSection,
        getPage,
        getPages,
        getPlacesWhereItemIsPresent,
        removeItemFromSection
    } from "$lib/pagebuilder";
    import {NostrGlobalConfig} from "$sharedLib/stores";
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import Minus from "$sharedLib/components/icons/Minus.svelte";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";

    export let itemId;
    export let entityName;
    export let classOverride = "text-black dark:text-white";
    export let showAddActions = true;
</script>

{#if Object.keys($NostrGlobalConfig).length > 0}
    <hr class="mt-1 md:mt-0">

    <div class="flex mt-1 md:mt-4 items-start text-left text-sm md:text-md {classOverride}">
        <p class="opacity-75 mr-1 md:mr-2">Admin actions:</p>
        <div class="tooltip tooltip-top mr-1 md:mr-2 hidden md:block" data-tip="This is shown because you're an admin. Your visitors will not see this section.">
            <InfoIcon />
        </div>
        {#if showAddActions}
            <div class="dropdown dropdown-bottom">
                <div tabindex="0" class="tooltip tooltip-primary tooltip-top flex" data-tip="Add this to section">
                    <span class="w-5 md:w-6 text-green-500 cursor-pointer tooltip tooltip-primary tooltip-right text-left left">
                        <Plus />
                    </span>
                </div>
                <ul tabindex="0" class="dropdown-content menu shadow bg-base-300 rounded-box w-80 rounded border border-gray-400 z-[100]">
                    {#each Object.entries(getPages($NostrGlobalConfig)) as [pageId, page]}
                        {#each Object.entries(getPage(pageId).sections) as [sectionId, section]}
                            {#if section?.params?.sectionType && section?.params?.sectionType.includes(entityName)}
                                <li><a on:click={() => {addItemToSection(pageId, sectionId, itemId, entityName); document.activeElement.blur()}}>{page.title} - {section.title}</a></li>
                            {/if}
                        {/each}
                    {/each}
                </ul>
            </div>
        {/if}
    </div>

    <div class="aaaflex mt-1 md:mt-3 items-start text-left text-sm md:text-md {classOverride}">
        {#each Object.entries(getPlacesWhereItemIsPresent(itemId, entityName, $NostrGlobalConfig)) as [placeId, placeTitle]}
            <div class="w-max flow mb-0 opacity-75">
                <span class="w-5 md:w-6 text-rose-500 cursor-pointer tooltip tooltip-primary tooltip-right"
                      data-tip="Remove this from section"
                      on:click|preventDefault={() => removeItemFromSection(placeId.split('-')[0], placeId.split('-')[1], itemId, entityName)}
                >
                    <Minus />
                </span>
                <span class="md:ml-1 align-top">{placeTitle}</span>
            </div>
        {/each}
    </div>
{/if}
