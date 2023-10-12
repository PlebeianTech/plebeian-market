<script lang="ts">
    import type { Item } from "$lib/types/item";
    import Gallery from "$lib/components/Gallery.svelte";

    const MAX_MEDIA_COUNT = 10;

    export let item: Item;

    let fileinput;
	function onFileSelected (e) {
        let reader = new FileReader();
        reader.readAsDataURL(e.target.files[0]);
        reader.onload = (r) => {
            if (r.target && (typeof r.target.result === 'string')) {
                item.added_media = [...item.added_media, {file: e.target.files[0], url: r.target.result}];
            }
        };
    }
</script>

<div class="form-control mr-2 mt-4 w-full flex flex-row">
    <div class="w-1/2">
        {#if item.media.length === 0 && item.added_media.length === 0}
            <p class="text-xl">Add some pictures...</p>
        {/if}
        {#if item.media.length + item.added_media.length < MAX_MEDIA_COUNT}
            <div class="w-full mt-4">
                <input type="file" accept=".jpg, .jpeg, .png" class="file-input file-input-lg file-input-primary w-full max-w-xs" on:change={onFileSelected} bind:this={fileinput} />
            </div>
        {/if}
    </div>
    <div class="w-1/2">
        {#if item.media.length !== 0 || item.added_media.length !== 0}
            <h3 class="text-xl">Media</h3>
            <Gallery photos={item.media.concat(item.added_media)} />
        {/if}
    </div>
</div>
