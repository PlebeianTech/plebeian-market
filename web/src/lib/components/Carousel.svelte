<script lang="ts">
    import type { Media } from "../types/auction";

    export let photos: Media[];
</script>

<div class="mt-4 carousel w-full">
    {#each photos as photo, i}
        <div id="{photo.twitter_media_key}" class="carousel-item relative w-full">
            <img src={photo.url} alt="Auctioned object" />
            <div class="absolute flex justify-between transform -translate-y-1/2 left-5 right-5 top-1/2">
                {#if i}
                    <a href="#{photos[i - 1].twitter_media_key}" class="btn btn-circle">❮</a>
                {:else}
                    <a href={null} class="">&nbsp;</a>
                {/if}
                {#if i < photos.length - 1}
                    <a href="#{photos[i + 1].twitter_media_key}" class="btn btn-circle">❯</a>
                {:else}
                    <a href={null} class="">&nbsp;</a>
                {/if}
            </div>
        </div>
    {/each}
</div>
<div class="mb-4 flex justify-center w-full py-2 gap-2">
    {#each photos as photo, i}
        <a href="#{photo.twitter_media_key}" class="btn btn-xs">{i + 1}</a>
    {/each}
</div>