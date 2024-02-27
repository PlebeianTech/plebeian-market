<script lang="ts">
    import Nostr from "$lib/components/settings/Nostr.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
</script>

<svelte:head>
    <title>Nostr Information</title>
</svelte:head>

<Titleh1>Nostr Information</Titleh1>

<div class="flex w-full 2xl:w-10/12 3xl:w-8/12 p-0 md:p-4 pb-8 mx-auto">
    <div class="mx-auto">
        <Nostr />
    </div>
</div>
