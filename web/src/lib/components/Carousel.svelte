<script lang="ts">
    import type { Media } from "../types/auction";

    export let photos: Media[];
</script>

<div class="mt-4 carousel carousel-center space-x-4">
    {#each photos as photo, i}
        <div id="{photo.twitter_media_key}" class="carousel-item">
            <img class="h-96 w-48 lg:w-96 object-scale-down" src={photo.url} alt="Auctioned object" />
        </div>
    {/each}
</div>

<div class="invisible lg:visible h-0 mb-4 flex justify-center w-full py-2 gap-2">
    {#each photos as photo, i}
        <a href="#{photo.twitter_media_key}" class="btn btn-xs">{i + 1}</a>
    {/each}
</div>
