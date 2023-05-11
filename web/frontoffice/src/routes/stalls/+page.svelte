<script lang="ts">
    import Browse from "$lib/components/stores/Browse.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
</script>

<svelte:head>
    <title>Stall Browser</title>
</svelte:head>

<Titleh1>List of nip-15 compatible stores</Titleh1>

<Browse merchantPubkey={null}></Browse>
