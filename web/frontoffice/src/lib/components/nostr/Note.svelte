<script lang="ts">
    import type { VitaminedMessage } from "$lib/components/nostr/types";
    import NostrNoteActions from "$lib/components/nostr/NoteActions.svelte";
    import NostrReplyNote from "$lib/components/nostr/ReplyNote.svelte";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";
    import ImagePreview from "$lib/components/nostr/ImagePreview.svelte";
    import {formatTimestamp} from '$lib/nostr/utils';
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    export let message: VitaminedMessage;
    export let onReply = (_) => {};
    export let onImgError = (_imgElement, _message) => {};

    $: profilePicture = message.profile && message.profile.picture ? message.profile.picture : profilePicturePlaceHolder;
    $: displayName = message.profile && message.profile.name ? message.profile.name : (message.pubkey ? message.pubkey.slice(0, 8) : "");
</script>

<div class="flex py-2 overflow-hidden" class:mt-0={message.samePubKey} class:mt-3={!message.samePubKey} class:profileInfo={!message.samePubKey} data-note-id="{message.id}">
    <!-- AVATAR -->
    <div>
        <div class="chat-image avatar">
            <div class="w-14 ml-4 lg:mr-4 rounded-full">
                {#if !message.samePubKey}
                    <img src="{profilePicture}" on:error={(event) => onImgError(event.srcElement, message)} alt="avatar" class:profileInfoImage={!message.samePubKey} />
                {/if}
            </div>
        </div>
    </div>

    <div class="items-center w-full border-b border-gray-600 px-4">
        <!-- NAME, BADGES, DATE -->
        <div class="space-y-1">
            {#if !message.samePubKey}
                <div class="chat-header flex items-center">
                    <p class="mr-3" class:profileInfoName={!message.samePubKey}>{displayName}</p>
                    {#if message.nip05VerifiedAddress}
                        <Nip05Checkmark {message}></Nip05Checkmark>
                    {/if}
                </div>
            {/if}
            <div class="text-xs opacity-50">{formatTimestamp(message.created_at)}</div>
        </div>

        <!-- REPLY TO -->
        {#if message.repliedToMessage}
            <div class="card card-compact border border-gray-400/70 my-3 shadow-xl">
                <NostrReplyNote message={message.repliedToMessage} />
            </div>
        {/if}

        <!-- MESSAGES AND ICONS -->
        <div class="mt-2 mb-1 whitespace-pre-wrap" style="word-break: break-word;">{@html message.content}</div>

        {#if message.imagePreviewUrl}
            <ImagePreview imagePreviewUrl={message.imagePreviewUrl}></ImagePreview>
        {/if}

        <NostrNoteActions {message} {onReply} />
    </div>
</div>
