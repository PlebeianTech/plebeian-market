<script lang="ts">
    import {onMount} from "svelte";
    import SvelteMarkdown from 'svelte-markdown'
    import {subscribeConfiguration, getConfigurationKey} from "$sharedLib/services/nostr";
    import {fileConfiguration} from "$sharedLib/stores";

    export let pageId;
    export let sectionId;

    let markdownText: string | null = null;

    onMount(async () => {
        if ($fileConfiguration && $fileConfiguration.admin_pubkeys.length > 0) {
            let receivedAt = 0;

            subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('sectionText_' + pageId + '_' + sectionId)],
                (markdownTextForSection, rcAt) => {
                    if (rcAt > receivedAt) {
                        receivedAt = rcAt;
                        markdownText = markdownTextForSection;
                    }
                });
        }
    });
</script>

<main class="mx-auto px-8 md:container">
    {#if !markdownText}
        <div class="p-12 flex flex-wrap items-center justify-center">
            <span class="loading loading-bars w-24"></span>
        </div>
    {:else}
        <div class="z-[300] prose lg:prose-xl">
            <SvelteMarkdown source={markdownText} />
        </div>
    {/if}
</main>
