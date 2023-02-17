<script lang="ts">
    import NostrNoteActions from "$lib/components/nostr/NoteActions.svelte";
    import NostrReplyNote from "$lib/components/nostr/ReplyNote.svelte";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";
    import {formatTimestamp} from '$lib/nostr/utils';
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    export let pool;
    export let message;
    export let onReply;
</script>

<div class="flex py-2" class:mt-0={message.samePubKey} class:mt-5={!message.samePubKey} class:profileInfo={!message.samePubKey} data-note-id="{message.id}">

    <!-- AVATAR -->
    <div class="">
        <div class="chat-image avatar">
            <div class="w-14 mx-4 rounded-full ring-primary ring-offset-base-100 ring-offset-1" class:ring={!message.samePubKey}>
                {#if !message.samePubKey}
                    <img src="{message.profileImage ?? profilePicturePlaceHolder}" alt="profile picture" class:profileInfoImage={!message.samePubKey} />
                {/if}
            </div>
        </div>
    </div>

    <div class="items-center w-full border-b border-gray-600 px-4">
        <!-- NAME, BADGES, DATE -->
        <div class="space-y-1">
            {#if !message.samePubKey}
                <div class="chat-header flex items-center">
                    <p class="mr-3" class:profileInfoName={!message.samePubKey}>{message.profileName ?? message.pubkey.slice(0, 8)}</p>
                    {#if message.nip05}
                        <Nip05Checkmark {message}></Nip05Checkmark>
                    {/if}
                </div>
            {/if}
            <div class="text-xs opacity-50">{formatTimestamp(message.created_at)}</div>
        </div>

        <div class="">
            <!-- REPLY TO -->
            {#if message.repliedToMessage}
                <div class="card card-compact border border-gray-400/70 my-4 shadow-xl">
                    {#if typeof message.repliedToMessage === 'object'}
                        <NostrReplyNote message={message.repliedToMessage}></NostrReplyNote>
                    {:else}
                        <div class="py-4 px-4">Replying to #{message.repliedToMessage.slice(0, 8)}</div>
                    {/if}
                </div>
            {/if}

            <!-- MESSAGES AND ICONS -->
            <div class="my-4">{@html message.content}</div>
            <NostrNoteActions {pool} {message} {onReply}></NostrNoteActions>
        </div>
    </div>
</div>
