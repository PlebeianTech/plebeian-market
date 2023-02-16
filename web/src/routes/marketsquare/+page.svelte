<svelte:head>
    <title>Market Square</title>
</svelte:head>

<script lang="ts">
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import { isProduction } from "$lib/utils";
    import { pmChannelNostrRoomId } from '$lib/nostr/pool'
</script>

<div class="lg:w-2/3 mx-auto lg:p-0 p-2">
    <div class="py-8">
        {#if !isProduction() }
            <NostrChat
                messageLimit={75}
                nostrRoomId={pmChannelNostrRoomId}
            />
        {/if}
    </div>
</div>
