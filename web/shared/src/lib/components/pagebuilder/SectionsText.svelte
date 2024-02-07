<script lang="ts">
    import {onMount} from "svelte";
    import {subscribeConfiguration, getConfigurationKey} from "$sharedLib/services/nostr";
    import {fileConfiguration} from "$sharedLib/stores";
    import RichTextComposer from "$sharedLib/components/pagebuilder/lexical-editor/RichTextComposer.svelte";
    //import {transformLexicalJSONToHTML} from "@bowline/svelte-lexical/src/transform-json-to-html";
    // import {getHtmlFromLexicalJSON} from "$sharedLib/components/pagebuilder/lexical-editor/transform-json-to-html";
    //import {fromArrayPack, unminify} from "lexical-minifier";
    import '$sharedLib/components/pagebuilder/lexical-editor/lexical.css';

    export let pageId;
    export let sectionId;

    let initialMinifiedLexicalContent: string | null = null;
//    let lexicalHtml: string | null = null;

    onMount(() => {
        if ($fileConfiguration?.admin_pubkeys?.length > 0) {
            let receivedAt = 0;

            subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('sectionText_' + pageId + '_' + sectionId)],
                (initialMinifiedLexicalContentFromNostr, rcAt) => {
                    if (rcAt > receivedAt) {
                        receivedAt = rcAt;
                        initialMinifiedLexicalContent = initialMinifiedLexicalContentFromNostr;

                        // let jsonParsed = JSON.parse(initialMinifiedLexicalContent);
                        // let arrayUnpacked = fromArrayPack(jsonParsed);
                        // let unminified = unminify(arrayUnpacked) ?? [];
                        // lexicalHtml = transformLexicalJSONToHTML(JSON.stringify({ root: unminified } ?? []));
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
        <!--
        <div class="z-[300] lexical-div aaprose w-full lg:11/12 xl:w-9/12 2xl:w-7/12 mx-auto">
            {@html lexicalHtml}
        </div>
        -->
    {/if}
</main>
