<script lang="ts">
    import {onDestroy} from "svelte";
    import {Pool} from "$lib/nostr/pool";
    import {getChannelIdForStallOwner, pmChannelNostrRoomId} from '$lib/nostr/utils'
    import {user} from "$lib/stores";

    export let pmURL: string | null;

    const pool: Pool = new Pool();

    function postToNostr(location: 'stall' | 'mktSquare' | 'nostrFeed') {
        let message;

        let nostrRoomId;
        switch (location) {
            case 'stall':
                message = 'Hi people! I just listed a new product. Give it a look:';
                nostrRoomId = getChannelIdForStallOwner($user);
                break;
            case 'mktSquare':
                message = 'Hey! Check the new product I just created!';
                nostrRoomId = pmChannelNostrRoomId;
                break;
            case 'nostrFeed':
                message = 'Check the product I just published at Plebeian Market!';
                nostrRoomId = false;
                break;
        }

        message += '\n' + pmURL;

        pool.connectAndSendMessage({
            message,
            user,
            nostrRoomId,
        });
    }

    onDestroy(() => {
        pool.disconnect();
    })
</script>

<a href="#anchorId" on:click|preventDefault={() => postToNostr("stall")} class="btn align-middle bg-blue-500 hover:bg-indigo-500 mb-2">
    <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
        <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
    </svg>

    Post to My Stall
</a>

<a href="#anchorId" on:click|preventDefault={() => postToNostr("mktSquare")} class="btn align-middle bg-blue-500 hover:bg-indigo-500 mb-2">
    <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
        <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
    </svg>

    Post to Market Square
</a>

<a href="#anchorId" on:click|preventDefault={() => postToNostr("nostrFeed")} class="btn align-middle bg-blue-500 hover:bg-indigo-500 mb-2">
    <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
        <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
    </svg>

    Share in my Nostr feed
</a>
