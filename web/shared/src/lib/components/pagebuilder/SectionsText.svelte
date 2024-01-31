<script lang="ts">
    import {onMount} from "svelte";
    import {subscribeConfiguration, getConfigurationKey} from "$sharedLib/services/nostr";
    import {fileConfiguration} from "$sharedLib/stores";
    import RichTextComposer from "$sharedLib/components/pagebuilder/lexical-editor/RichTextComposer.svelte";

    export let pageId;
    export let sectionId;

    let initialMinifiedLexicalContent: string | null = null;

    onMount(async () => {
        if ($fileConfiguration && $fileConfiguration.admin_pubkeys.length > 0) {
            let receivedAt = 0;

            subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('sectionText_' + pageId + '_' + sectionId)],
                (initialMinifiedLexicalContentFromNostr, rcAt) => {
                    if (rcAt > receivedAt) {
                        receivedAt = rcAt;
                        initialMinifiedLexicalContent = initialMinifiedLexicalContentFromNostr;
                    }
                });
        }
    });
</script>

<main class="mx-auto px-8 md:container">
    {#if !initialMinifiedLexicalContent}
        <div class="p-12 flex flex-wrap items-center justify-center">
            <span class="loading loading-bars w-24"></span>
        </div>
    {:else}
        <div class="z-[300]">
            <RichTextComposer {initialMinifiedLexicalContent} editable={false} />
        </div>
    {/if}
</main>
