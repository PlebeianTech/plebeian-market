<script lang="ts">
    import SvelteMarkdown from 'svelte-markdown';

    export let placeholder: string = "";
    export let value: string;

    let currentTab = "Description";
    let markdownEditor;

    function addBold() {
        injectNewMarkdown("**** ", true);
        markdownEditor.focus();
    }

    function addHeader2() {
        if ( markdownEditor.selectionStart === 0 || lineIsEmpty()) {
            injectNewMarkdown("## ")
        } else {
            injectNewMarkdown("\n## ");
        }
        markdownEditor.focus();
    }

    function addItalic() {
        injectNewMarkdown("** ", true);
        markdownEditor.focus();
    }

    function addListItem() {
        // adds a new line item at cursor
        if (lineIsEmpty() ) {
            injectNewMarkdown("- ");
        } else {
            injectNewMarkdown("\n- ");
        }
        markdownEditor.focus();
    }

    function injectNewMarkdown(text, cursorPositionMiddle=false) {
        /* Injects markdown text into textarea and positions cursor */
        let walkback = text.length;
        if ( cursorPositionMiddle ) {
            walkback = Math.floor(text.length / 2);
        }
        let cursorPosition = markdownEditor.selectionStart;
        let beforeNewText = markdownEditor.value.slice(0, cursorPosition);
        let afterNewText = markdownEditor.value.slice(cursorPosition);
        markdownEditor.value = [beforeNewText, text, afterNewText].join('');
        let newCursorPosition = cursorPosition + walkback;
        moveCursorToPosition(newCursorPosition);
    }

    function lineIsEmpty() {
        let cursorPosition = markdownEditor.selectionStart;
        let startLineIndex = markdownEditor.value.lastIndexOf("\n", cursorPosition - 1);
        let line = markdownEditor.value.substring(startLineIndex, cursorPosition);
        // empty line has a length of 1
        if (line.length > 1) {
            return false
        }
        return true;
    }


    function manageTextInput(e) {
        /* Manage all text input here.
           Currently:
            - adding new list items automatically on enter
        */
        if ( e.key === "Enter" ) {
            let cursorPosition = markdownEditor.selectionStart;
            let startLineIndex = markdownEditor.value.lastIndexOf("\n", cursorPosition - 1);
            let line = markdownEditor.value.substring(startLineIndex, cursorPosition);
            if (line.trim() === "-") {
                e.preventDefault();
                cursorPosition = markdownEditor.selectionStart;
                replaceListItemWithEmptyLine(startLineIndex, cursorPosition);
            } else if (line.trim().startsWith("-")) {
                e.preventDefault();
                addListItem();
            }
        }
    }

    function moveCursorToPosition(cursorPosition) {
        markdownEditor.selectionStart = cursorPosition;
        markdownEditor.selectionEnd = cursorPosition;
    }

    function replaceListItemWithEmptyLine(startLineIndex, position) {
        /* When a user hits enter on a line with an empty list item
           makes the line empty */
        let emptyListItemStart = markdownEditor.value.slice(0, startLineIndex);
        let emptyListItemEnd = markdownEditor.value.slice(position + 1);
        markdownEditor.value = [emptyListItemStart, emptyListItemEnd].join('\n\n');
        markdownEditor.selectionEnd = position - 2;
        markdownEditor.focus();
    }
</script>

<div class="tabs justify-center mb-4 mt-2">
    {#each ['Description', 'Preview'] as tab}
        <li class="tab tab-bordered mt-0 mr-5 text-lg cursor-pointer" class:tab-active={tab === currentTab} on:click={() => currentTab = tab}>
            <div>{tab}</div>
        </li>
    {/each}
</div>

{#if currentTab === 'Description'}
    <div class="form-control">
        <!-- Text Editor Buttons -->
        <div class="flex m-auto mb-4">
            <div class="btn rounded-full mx-1 lg:mb-0 mb-1 btn-secondary" on:click={addHeader2}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-type-h2" viewBox="0 0 16 16">
                    <path d="M7.638 13V3.669H6.38V7.62H1.759V3.67H.5V13h1.258V8.728h4.62V13h1.259zm3.022-6.733v-.048c0-.889.63-1.668" />
                </svg>
            </div>
            <div class="btn rounded-full mx-1 lg:mb-0 mb-1 btn-secondary" on:click={addBold}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-type-bold" viewBox="0 0 16 16">
                    <path d="M8.21 13c2.106 0 3.412-1.087 3.412-2.823 0-1.306-.984-2.283-2.324-2.386v-.055a2.176 2.176 0 0 0 1.852-2.14c0-1.51-1.162-2.46-3.014-2.46H3.843V13H8.21zM5.908 4.674h1.696c.963 0 1.517.451 1.517 1.244 0 .834-.629 1.32-1.73 1.32H5.908V4.673zm0 6.788V8.598h1.73c1.217 0 1.88.492 1.88 1.415 0 .943-.643 1.449-1.832 1.449H5.907z"/>
                </svg>
            </div>
            <div class="btn rounded-full mx-1 lg:mb-0 mb-1 btn-secondary" on:click={addItalic}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-type-italic" viewBox="0 0 16 16">
                    <path d="M7.991 11.674 9.53 4.455c.123-.595.246-.71 1.347-.807l.11-.52H7.211l-.11.52c1.06.096 1.128.212 1.005.807L6.57 11.674c-.123.595-.246.71-1.346.806l-.11.52h3.774l.11-.52c-1.06-.095-1.129-.211-1.006-.806z"/>
                </svg>
            </div>
            <div class="btn rounded-full mx-1 lg:mb-0 mb-1 btn-secondary" on:click={addListItem}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-list-ul" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M5 11.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm-3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 4a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm0 4a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/>
                </svg>
            </div>
        </div>
        <small class="pt-2 fg-neutral-content mb-1">Markdown accepted</small>
        <textarea on:keydown={manageTextInput} bind:this={markdownEditor} bind:value={value} rows="6" class="textarea textarea-bordered h-48" {placeholder}></textarea>
    </div>
{:else if currentTab === 'Preview'}
    <div class="p-2">
        <div class="markdown-container bg-base-100 rounded-md p-2">
            <SvelteMarkdown source={value} />
        </div>
    </div>
{/if}