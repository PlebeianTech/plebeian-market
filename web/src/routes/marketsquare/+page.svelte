<svelte:head>
    <title>Market Square</title>
</svelte:head>

<script lang="ts">
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import { pmChannelNostrRoomId } from '$lib/nostr/pool'
</script>

<div class="px-2 pb-4 mx-auto w-screen lg:w-2/3">
    <h1 class="text-3xl lg:text-6xl fontbold mt-0 lg:mt-8 mb-2">Market Square</h1>

    <NostrChat
        messageLimit={75}
        nostrRoomId={pmChannelNostrRoomId}
        fixedChatBox={true}
    />
</div>
