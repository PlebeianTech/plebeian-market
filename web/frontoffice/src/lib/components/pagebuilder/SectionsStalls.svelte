<script lang="ts">
    import {onMount} from "svelte";
    import {refreshStalls} from "$lib/shopping";
    import {getItemsFromSection} from "$lib/pagebuilder";
    import {fileConfiguration, isSuperAdmin, NostrGlobalConfig, stalls} from "$sharedLib/stores";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import AdminActions from "$lib/components/pagebuilder/AdminActions.svelte";

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
                <a href="/p/{$stalls.stalls[stallId].merchantPubkey}/stall/{$stalls.stalls[stallId].id}">
                    <div class="bg-white dark:bg-black rounded-lg shadow-md">
                        <div class="p-4 md:p-8" class:md:pb-2={$isSuperAdmin}>
                            <div class="cursor-pointer">
                                <div class="float-left h-7 w-7 mr-3"><Store /></div>
                                <h3 class="text-lg font-semibold">
                                    {#if $stalls.stalls[stallId].name}{$stalls.stalls[stallId].name}{/if}
                                </h3>
                                <p class="mt-2 lg:mt-3 text-gray-600 dark:text-gray-400 {$stalls.stalls[stallId].description && $stalls.stalls[stallId].description.length > descriptionLength ? 'tooltip tooltip-primary text-left' : ''}" data-tip={$stalls.stalls[stallId].description && $stalls.stalls[stallId].description.length > descriptionLength ? $stalls.stalls[stallId].description : ''}>
                                    {#if $stalls.stalls[stallId].description}{$stalls.stalls[stallId].description.substring(0,descriptionLength)}{#if $stalls.stalls[stallId].description.length > descriptionLength}...{/if}{/if}
                                </p>
                            </div>

                            {#if $isSuperAdmin && $NostrGlobalConfig}
                                <a href={null} on:click|preventDefault>
                                    <div class="p-0 md:p-4 md:pb-0 cursor-default">
                                        <AdminActions
                                            itemId={stallId}
                                            entityName="stalls"
                                        />
                                    </div>
                                </a>
                            {/if}
                        </div>
                    </div>
                </a>
            {/if}
        {/each}

        {#if $fileConfiguration.backend_present}
            <div class="bg-white dark:bg-black rounded-lg shadow-md">
                <div class="p-4 md:p-8">
                    <a href="/admin">
                        <div class="cursor-pointer">
                            <div class="float-left h-7 w-7 mr-3"><Store /></div>
                            <h3 class="text-lg font-semibold">
                                Create your stall here!
                            </h3>
                            <p class="mt-2 lg:mt-3 text-gray-600 dark:text-gray-400">
                                Do you want to sell or auction your own products? Create your stall now!
                            </p>
                        </div>
                    </a>
                </div>
            </div>
        {/if}
    </div>
</main>
