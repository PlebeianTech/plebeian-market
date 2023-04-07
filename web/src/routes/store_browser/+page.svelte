<script lang="ts">
    import Browse from "$lib/components/stores/Browse.svelte";
</script>

<svelte:head>
    <title>Store Browser</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-12 lg:mb-12 p-4">List of nip-05 compatible stores</h1>

<div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">
    <Browse merchantPubkey={null}></Browse>
</div>
