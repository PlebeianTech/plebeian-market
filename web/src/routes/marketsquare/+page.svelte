<svelte:head>
    <title>Market Square</title>
</svelte:head>

<script lang="ts">
    import NostrChat from "$lib/components/NostrChat.svelte";
    import { isProduction } from "$lib/utils";
    import { pmChannelNostrRoomId } from '$lib/nostr/utils'

    let roomData = {
        name: 'Plebeian Market Square',
        about: 'You can discuss here all matters related with Plebeian Market.',
        picture: 'https://staging.plebeian.market/images/new-logo.svg'
    }
</script>

<div class="flex mb-20 ml-60 mr-60">
    {#if !isProduction() }
        <div>
            <NostrChat
                {roomData}
                emptyChatShowsLoading={true}
                messageLimit={200}
                messagesSince={1672837281}
                nostrRoomId={pmChannelNostrRoomId}
            />
        </div>
    {/if}
</div>
