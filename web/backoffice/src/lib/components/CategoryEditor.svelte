<script lang="ts">
    import type { Item } from "$lib/types/item";
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import X from "$sharedLib/components/icons/X.svelte";

    export let item: Item;

    let newCategory = "";

    function addCategory() {
        if (newCategory !== "") {
            item.categories = [...item.categories, newCategory];
            newCategory = "";
        }
    }

    function removeCategory(i) {
        item.categories = item.categories.slice(0, i).concat(item.categories.slice(i + 1));
    }
</script>

<div class="form-control mr-2 mt-4 w-full flex">
    <p class="text-xl my-2">Categories...</p>
    {#each item.categories as category, i}
        <div class="mt-3">
            <div class="badge badge-primary badge-lg align-top">{category}</div>
            <div class="btn btn-circle btn-xs btn-error ml-1" on:click={() => removeCategory(i)} on:keypress={() => removeCategory(i)}><X /></div>
        </div>
    {/each}
    <div class="form-control w-full flex flex-row">
        <div>
            <input bind:value={newCategory} type="text" name="new-category" class="input input-bordered w-full max-w-xs" />
        </div>
        <div>
            <button class="btn btn-s btn-circle btn-ghost mx-4" on:click={addCategory}><Plus /></button>
        </div>
    </div>
</div>