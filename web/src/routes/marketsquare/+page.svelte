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

<div class="lg:w-2/3 mx-auto py-4 lg:p-0 p-2">
    <div class="">
        {#if !isProduction() }
            <NostrChat
                {roomData}
                messageLimit={75}
                nostrRoomId={pmChannelNostrRoomId}
            />
        {/if}
    </div>
</div>
