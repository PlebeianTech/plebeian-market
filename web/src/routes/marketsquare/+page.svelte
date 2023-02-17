<svelte:head>
    <title>Market Square</title>
</svelte:head>

<script lang="ts">
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import { pmChannelNostrRoomId } from '$lib/nostr/pool'
</script>

<div class="lg:w-2/3 mx-auto lg:p-0 p-2">
  <h1 class="lg:text-6xl text-3xl font-bold lg:mt-8 mt-4">Plebeian Market Square</h1>
    <div class="py-4">
        <NostrChat
            messageLimit={75}
            nostrRoomId={pmChannelNostrRoomId}
        />
    </div>
</div>
