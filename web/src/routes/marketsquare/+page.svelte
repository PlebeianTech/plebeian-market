<svelte:head>
    <title>Market Square</title>
</svelte:head>

<script lang="ts">
    import NostrChat from "$lib/components/nostr/Chat.svelte";
    import { isProduction } from "$lib/utils";
    import { pmChannelNostrRoomId } from '$lib/nostr/utils'

    const roomData = {
        name: 'Plebeian Market Square',
        about: 'You can discuss here all matters related with Plebeian Market.',
        picture: 'https://staging.plebeian.market/images/new-logo.svg'
    }
</script>

<div class="grid mb-10 ml-2 mr-2 grid-cols-1 md:grid-cols-3">
    <div class="col-span-3 md:col-start-2 md:col-span-1">
        {#if !isProduction() }
            <NostrChat
                {roomData}
                messageLimit={75}
                nostrRoomId={pmChannelNostrRoomId}
            />
        {/if}
    </div>
</div>
