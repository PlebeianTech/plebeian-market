<script lang="ts">
    import type { Media } from "../types/auction";

    export let photos: Media[];
</script>

<div class="mt-4 carousel carousel-center space-x-4">
    {#each photos as photo, i}
        <div id="{photo.twitter_media_key}" class="carousel-item">
            <img class="h-96 w-48 object-cover rounded-md" src={photo.url} alt="Auctioned object" />
        </div>
    {/each}
</div>