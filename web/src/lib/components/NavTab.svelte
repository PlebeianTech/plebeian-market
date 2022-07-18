<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    export let items;
    export let activeItem;
</script>

<div class="mb-5 mt-5">
    <ul class="mt-0 flex justify-center p-0 list-none">
        {#each items as item}
            <li class="mt-0 mr-16 text-lg cursor-pointer" on:click={() => dispatch('tabChange', item)}>
                <div class:active={item === activeItem}>{item}</div>
            </li>
        {/each}
    </ul>
</div>

<style>
    .active {
        border-bottom: 2px solid gray;
        padding-bottom: 2px;
    }
</style>
