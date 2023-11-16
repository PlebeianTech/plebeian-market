<script lang="ts">
    import {formatTimestamp} from '$sharedLib/nostr/utils';

    export let message;
</script>

<div class="chat mt-0 md:mt-4" class:chat-start={!message.my_message_replying_to_this_pubkey} class:chat-end={message.my_message_replying_to_this_pubkey}>
    <div class="chat-bubble max-w-[80%] lg:max-w-[60%] text-white" class:chat-bubble-primary={!message.my_message_replying_to_this_pubkey} class:chat-bubble-accent={message.my_message_replying_to_this_pubkey}>
        {@html message.message}
        <div class="space-y-1 text-xs opacity-60 text-right mt-1">{formatTimestamp(message.created_at)}</div>
    </div>
</div>
