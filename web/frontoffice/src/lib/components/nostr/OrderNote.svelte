<script lang="ts">
    import {formatTimestamp} from '$sharedLib/nostr/utils';

    export let message;
</script>



<div class="chat mt-4" class:chat-start={message.sender === undefined} class:chat-end={message.sender !== undefined}>
    <div class="chat-bubble max-w-[80%] lg:max-w-[60%]" class:chat-bubble-primary={message.sender === undefined} class:chat-bubble-success={message.sender !== undefined}>
        {JSON.stringify(message)}
        {#if message.type == 1}
            <p>New order send.</p>
            <p>Waiting reply from the stall.</p>
        {:else if message.type == 2}
            <p>2222222222222</p>
        {:else if message.type == 3}
            <p>3333333333333</p>
        {:else}
        {/if}
        <div class="space-y-1 text-xs opacity-60 text-right mt-1">{formatTimestamp(message.created_at)}</div>
    </div>
</div>
