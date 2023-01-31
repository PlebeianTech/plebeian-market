<script lang="ts">
    import {formatTimestamp} from '$lib/nostr/utils';
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg?url";

    export let message;
</script>

<div class="chat chat-start" class:mt-0={message.samePubKey} class:mt-5={!message.samePubKey} class:profileInfo={!message.samePubKey}>
    <div class="chat-image avatar">
        <div class="w-12 rounded-full ring-primary ring-offset-base-100 ring-offset-2" class:ring={!message.samePubKey}>
            {#if !message.samePubKey}
                <img src="{message.profileImage ?? profilePicturePlaceHolder}" alt="profile picture" class:profileInfoImage={!message.samePubKey} />
            {/if}
        </div>
    </div>
    {#if !message.samePubKey}
        <div class="chat-header">
            <span class="mr-3" class:profileInfoName={!message.samePubKey}>{message.profileName ?? message.pubkey.slice(0, 8)}</span>
        </div>
    {/if}
    <div class="chat-bubble">{@html message.content}</div>
    <div class="chat-footer text-xs opacity-50">{formatTimestamp(message.created_at)}</div>
</div>
