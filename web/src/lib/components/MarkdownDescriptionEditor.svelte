<script lang="ts">
    import { onMount } from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';

    const PLACEHOLDER = `## Heading 1
Text text text... **bold text**... *italic text* normal text normal text

### Heading 2
1. Ordered List
2. Ordered List
3. Ordered List

* Unordered List
* Unordered List
* Unordered List
`;

    export let value: string;

    let currentTab = "Description";

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
        <textarea bind:value={value} rows="6" class="textarea textarea-bordered h-48" placeholder=""></textarea>
        <small class="pt-2 fg-neutral-content">Markdown accepted</small>
    </div>
{:else if currentTab === 'Preview'}
    <div class="p-2">
        <div class="markdown-container bg-base-100 rounded-md p-2">
            <SvelteMarkdown source={value} />
        </div>
    </div>
{/if}