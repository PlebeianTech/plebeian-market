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

    export let itemId;
    export let entityName;
</script>

{#if Object.keys($NostrGlobalConfig).length > 0}
<div class="mt-3 md:mt-5 items-start text-left">
    <hr>

    <div class="flex mt-2 md:mt-4">
        <p class="opacity-75 mr-1 md:mr-2">Admin actions:</p>
        <div class="dropdown dropdown-bottom">
            <div tabindex="0" class="tooltip tooltip-primary tooltip-top flex" data-tip="Add this to section">
                <span class="w-6 text-green-500 cursor-pointer tooltip tooltip-primary tooltip-right text-left left">
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
    </div>

    <div class="flex mt-2 md:mt-3">
        {#each Object.entries(getPlacesWhereItemIsPresent(itemId, entityName, $NostrGlobalConfig)) as [placeId, placeTitle]}
            <div class="w-max flex mb-2 opacity-75">
                <span class="w-6 text-rose-500 cursor-pointer tooltip tooltip-primary tooltip-right"
                      data-tip="Remove this from section"
                      on:click|preventDefault={() => removeItemFromSection(placeId.split('-')[0], placeId.split('-')[1], itemId, entityName)}
                >
                    <Minus />
                </span>
                <span class="ml-1">{placeTitle}</span>
            </div>
        {/each}
    </div>
</div>
{/if}
