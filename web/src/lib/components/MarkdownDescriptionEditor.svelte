<script lang="ts">
    import { onMount } from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';

    const PLACEHOLDER = `## Heading 1
Text text text... **bold text**... *italic text* normal text normal text

### Heading 2
 - Unordered List
 - Unordered List
 - Unordered List
`;

    export let value: string;

    let currentTab = "Description";
    let markdownEditor;

    function addHeader2() {
        if ( markdownEditor.selectionStart === 0) {
            markdownEditor.value += "## ";
        } else {
            markdownEditor.value += "\n## ";
        }
        markdownEditor.focus();
    }

    function addHeader3() {
        if ( markdownEditor.selectionStart === 0) {
            markdownEditor.value += "### ";
        } else {
            markdownEditor.value += "\n### ";
        }
        markdownEditor.focus();
    }

    function addBold() {
        markdownEditor.value += "**** ";
        markdownEditor.selectionEnd -= 3;
        markdownEditor.focus();
    }

    function addItalic() {
        markdownEditor.value += "** ";
        markdownEditor.selectionEnd -= 2;
        markdownEditor.focus();
    }

    function addListItem() {
        markdownEditor.value += "\n- ";
        markdownEditor.focus();
    }

    onMount(async () => {
        if (value === "") {
            value = PLACEHOLDER;
        }
    });
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
        <div class="flex flex-wrap m-auto mb-4">
            <div class="btn rounded-full mx-1 lg:mb-0 mb-1 btn-secondary" on:click={addHeader2}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-type-h2" viewBox="0 0 16 16">
                    <path d="M7.638 13V3.669H6.38V7.62H1.759V3.67H.5V13h1.258V8.728h4.62V13h1.259zm3.022-6.733v-.048c0-.889.63-1.668 1.716-1.668.957 0 1.675.608 1.675 1.572 0 .855-.554 1.504-1.067 2.085l-3.513 3.999V13H15.5v-1.094h-4.245v-.075l2.481-2.844c.875-.998 1.586-1.784 1.586-2.953 0-1.463-1.155-2.556-2.919-2.556-1.941 0-2.966 1.326-2.966 2.74v.049h1.223z"/>
                </svg>
            </div>
            <div class="btn rounded-full mx-1 lg:mb-0 mb-1 btn-secondary" on:click={addHeader3}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-type-h3" viewBox="0 0 16 16">
                    <path d="M7.637 13V3.669H6.379V7.62H1.758V3.67H.5V13h1.258V8.728h4.62V13h1.259zm3.625-4.272h1.018c1.142 0 1.935.67 1.949 1.674.013 1.005-.78 1.737-2.01 1.73-1.08-.007-1.853-.588-1.935-1.32H9.108c.069 1.327 1.224 2.386 3.083 2.386 1.935 0 3.343-1.155 3.309-2.789-.027-1.51-1.251-2.16-2.037-2.249v-.068c.704-.123 1.764-.91 1.723-2.229-.035-1.353-1.176-2.4-2.954-2.385-1.873.006-2.857 1.162-2.898 2.358h1.196c.062-.69.711-1.299 1.696-1.299.998 0 1.695.622 1.695 1.525.007.922-.718 1.592-1.695 1.592h-.964v1.074z"/>
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
        <textarea bind:this={markdownEditor} bind:value={value} rows="6" class="textarea textarea-bordered h-48" placeholder=""></textarea>
        <small class="pt-2 fg-neutral-content">Markdown accepted</small>
    </div>
{:else if currentTab === 'Preview'}
    <div class="p-2">
        <div class="markdown-container bg-base-100 rounded-md p-2">
            <SvelteMarkdown source={value} />
        </div>
    </div>
{/if}