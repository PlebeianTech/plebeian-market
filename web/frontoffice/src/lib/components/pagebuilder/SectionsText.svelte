<script lang="ts">
    import {onMount} from "svelte";
    import SvelteMarkdown from 'svelte-markdown'
    import {getConfigurationKey} from "$lib/pagebuilder";
    import {subscribeConfiguration} from "$sharedLib/services/nostr";
    import {getConfigurationFromFile} from "$sharedLib/utils";

    export let pageId;
    export let sectionId;

    let markdownText: string | null = null;

    onMount(async () => {
        let config = await getConfigurationFromFile();

        if (config && config.admin_pubkeys.length > 0) {
            let receivedAt = 0;

            const configurationKey = getConfigurationKey(pageId, sectionId, 'sectionText');
            if (configurationKey) {
                subscribeConfiguration(config.admin_pubkeys, configurationKey,
                    (markdownTextForSection, rcAt) => {
                        if (rcAt > receivedAt) {
                            receivedAt = rcAt;
                            markdownText = markdownTextForSection;
                        }
                    });
            }
        }
    });
</script>

<main class="container mx-auto p-4 pt-0">
    {#if !markdownText}
        <div class="p-12 flex flex-wrap items-center justify-center">
            <span class="loading loading-bars w-24"></span>
        </div>
    {:else}
        <div class="z-[300] prose aadark:prose-invert lg:prose-xl">
            <SvelteMarkdown source={markdownText} />
        </div>
    {/if}
</main>
