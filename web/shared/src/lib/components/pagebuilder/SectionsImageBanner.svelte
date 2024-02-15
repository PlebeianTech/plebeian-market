<script lang="ts">
    export let section;
</script>

{#if section?.params?.imageBannerURL}
    <img class="w-full h-auto" src="{section?.params?.imageBannerURL}" alt="Banner Section" />
{/if}