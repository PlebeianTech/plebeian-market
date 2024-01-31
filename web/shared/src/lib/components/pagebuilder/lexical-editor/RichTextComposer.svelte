<script lang="ts">
    import type {SvelteComponent} from 'svelte';
    import {setContext, onMount} from 'svelte';
    import '$sharedLib/components/pagebuilder/lexical-editor/lexical.css';
    import {minify, unminify, toArrayPack, fromArrayPack} from 'lexical-minifier';
    import {
        Composer,
        ContentEditable,
        RichTextPlugin,
        SharedHistoryPlugin,
        ListPlugin,
        CheckListPlugin,
        HorizontalRulePlugin,
        ImagePlugin,
        AutoFocusPlugin,
        HeadingNode,
        QuoteNode,
        ListNode,
        ListItemNode,
        HorizontalRuleNode,
        ImageNode,
        TreeViewPlugin,
        PlaceHolder,
        HashtagPlugin,
        HashtagNode,
        AutoLinkPlugin,
        AutoLinkNode,
        LinkPlugin,
        LinkNode,
        validateUrl,
        FloatingLinkEditorPlugin,
        CodeNode,
        CodeHighlightNode,
        CodeHighlightPlugin,
        CodeActionMenuPlugin,
        CaptionEditorHistoryPlugin,
        CAN_USE_DOM,
    } from '@bowline/svelte-lexical';
    import type {LexicalEditor} from '@bowline/svelte-lexical';
    import PlaygroundEditorTheme from '$sharedLib/components/pagebuilder/lexical-editor/themes/PlaygroundEditorTheme';
    import ToolbarPlayground from '$sharedLib/components/pagebuilder/lexical-editor/ToolbarPlayground.svelte';
    import {createSettingsStore} from '$sharedLib/components/pagebuilder/lexical-editor/settings/setttingsStore';
    import {createEmptyRichText} from '$sharedLib/components/pagebuilder/lexical-editor/createEmptyRichText';

    const settings = createSettingsStore();
    setContext('settings', settings);

    export let editable: boolean = true;
    export let initialMinifiedLexicalContent = '';

    $: {
        if (composer && initialMinifiedLexicalContent) {
            let jsonParsed = JSON.parse(initialMinifiedLexicalContent);
            let arrayUnpacked = fromArrayPack(jsonParsed);
            let unminified = unminify(arrayUnpacked) ?? [];

            const editor = composer.getEditor() as LexicalEditor
            const editorState = editor.parseEditorState({ root: unminified });
            editor.setEditorState(editorState);
        }
    }

    export function getLexicalContent() {
        if (composer) {
            const editor = composer.getEditor() as LexicalEditor
            const state = editor.getEditorState();

            let lexicalContent = null;

            state.read(() => {
                const minified = minify(state._nodeMap.get('root'));
                lexicalContent = toArrayPack(minified);
            });

            return JSON.stringify(lexicalContent ?? []);
        }
    }

    let isSmallWidthViewport = true;

    let composer: SvelteComponent
    let editorDiv;

    const initialConfig = {
        editable: editable,
        editorState: createEmptyRichText,
        namespace: 'Playground',
        nodes: [
            HeadingNode,
            ListNode,
            ListItemNode,
            QuoteNode,
            HorizontalRuleNode,
            ImageNode,
            HashtagNode,
            AutoLinkNode,
            LinkNode,
            CodeNode,
            CodeHighlightNode,
        ],
        onError: (error: Error) => {
            throw error;
        },
//        onUpdate: () => {
//            console.log('onUpdate')
//        },
        theme: PlaygroundEditorTheme,
    };

    const updateEditable = () => {
        if (composer) {
            const editor = composer.getEditor() as LexicalEditor
            editor.setEditable($settings.isEditable);
        }
    };

    onMount(() => {
        function updateViewPortWidth() {
            const isNextSmallWidthViewport = CAN_USE_DOM && window.matchMedia('(max-width: 1025px)').matches;

            if (isNextSmallWidthViewport !== isSmallWidthViewport) {
                isSmallWidthViewport = isNextSmallWidthViewport;
            }
        }

        updateViewPortWidth();
        window.addEventListener('resize', updateViewPortWidth);

        return () => {
            window.removeEventListener('resize', updateViewPortWidth);
        };
    });
</script>

<div class="lexical-div">
    <Composer {initialConfig} bind:this={composer}>
        <div class="editor-shell">
            {#if editable}
                <ToolbarPlayground/>
            {/if}
            <div class="editor-container tree-view">
                <div class="editor-scroller" class:bg-[#fafafa]={editable}>
                    <div class="editor" bind:this={editorDiv}>
                        <ContentEditable/>
                        <PlaceHolder>Write the text you want to see in this section...</PlaceHolder>
                    </div>
                </div>

                <AutoFocusPlugin/>
                <HashtagPlugin/>
                <AutoLinkPlugin/>
                <RichTextPlugin/>
                <SharedHistoryPlugin/>
                <ListPlugin/>
                <CheckListPlugin/>
                <HorizontalRulePlugin/>
                <ImagePlugin>
                <CaptionEditorHistoryPlugin/>
                </ImagePlugin>
                <LinkPlugin {validateUrl}/>

                {#if !isSmallWidthViewport}
                    <FloatingLinkEditorPlugin anchorElem={editorDiv}/>
                    <CodeHighlightPlugin/>
                    <CodeActionMenuPlugin anchorElem={editorDiv}/>
                {/if}
            </div>
            {#if $settings.showTreeView}
                <TreeViewPlugin/>
            {/if}
        </div>
    </Composer>
</div>
