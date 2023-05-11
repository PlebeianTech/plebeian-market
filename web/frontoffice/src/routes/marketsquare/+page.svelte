<script lang="ts">
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import { pmChannelNostrRoomId } from "$lib/nostr/utils"
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
</script>

<svelte:head>
    <title>Market Square</title>
</svelte:head>

<Titleh1>Market Square</Titleh1>

<NostrChat messageLimit={75} nostrRoomId={pmChannelNostrRoomId} fixedChatBox={true} />
