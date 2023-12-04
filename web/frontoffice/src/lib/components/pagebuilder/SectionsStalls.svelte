<script lang="ts">
    import {onMount} from "svelte";
    import {refreshStalls} from "$lib/shopping";
    import {getItemsFromSection} from "$lib/pagebuilder";
    import {stalls} from "$sharedLib/stores";
    import Store from "$sharedLib/components/icons/Store.svelte";

    export let pageId;
    export let sectionId;

    let descriptionLength = 225;

    onMount(async () => {
        refreshStalls();
    });
</script>

<main class="p-4 md:container mx-auto pt-0">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-8 lg:gap-8 z-[300] mt-2 mb-2">
        {#each getItemsFromSection(pageId, sectionId, 'stalls') as stallId}
            {#if $stalls.stalls[stallId]}
                <div class="bg-white dark:bg-black rounded-lg shadow-md">
                    <div class="p-4 md:p-8">
                        <a href="/p/{$stalls.stalls[stallId].merchantPubkey}/stall/{$stalls.stalls[stallId].id}">
                            <div class="cursor-pointer">
                                <div class="float-left h-7 w-7 mr-3"><Store /></div>
                                <h3 class="text-lg font-semibold">
                                    {#if $stalls.stalls[stallId].name}{$stalls.stalls[stallId].name}{/if}
                                </h3>
                                <p class="mt-2 lg:mt-3 text-gray-600 dark:text-gray-400 {$stalls.stalls[stallId].description && $stalls.stalls[stallId].description.length > descriptionLength ? 'tooltip tooltip-primary text-left' : ''}" data-tip={$stalls.stalls[stallId].description && $stalls.stalls[stallId].description.length > descriptionLength ? $stalls.stalls[stallId].description : ''}>
                                    {#if $stalls.stalls[stallId].description}{$stalls.stalls[stallId].description.substring(0,descriptionLength)}{#if $stalls.stalls[stallId].description.length > descriptionLength}...{/if}{/if}
                                </p>
                            </div>
                        </a>
                    </div>
                </div>
            {/if}
        {/each}
    </div>
</main>
