<script lang="ts">
    import {formatTimestamp} from '$sharedLib/nostr/utils';

    export let message;
</script>

<div class="chat mt-0 md:mt-4" class:chat-start={message.sender === undefined} class:chat-end={message.sender !== undefined}>
    <div class="chat-bubble max-w-[80%] lg:max-w-[60%]" class:chat-bubble-primary={message.sender === undefined} class:chat-bubble-secondary={message.sender !== undefined}>
        {@html message.message}
        <div class="space-y-1 text-xs opacity-60 text-right mt-1">{formatTimestamp(message.created_at)}</div>
    </div>
</div>
