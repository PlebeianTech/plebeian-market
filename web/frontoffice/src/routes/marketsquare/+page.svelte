<script lang="ts">
    import { onMount } from 'svelte';
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import { getMarketSquareChannelId } from "$sharedLib/nostr/utils"
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";

    let nostrRoomId: string | null = null;

    onMount(async () => {
        nostrRoomId = await getMarketSquareChannelId();
    });
</script>

<svelte:head>
    <title>Market Square</title>
</svelte:head>

<Titleh1>Market Square</Titleh1>

{#if nostrRoomId !== null}
    <NostrChat messageLimit={75} {nostrRoomId} isMarketSquare={true} />
{/if}