<script lang="ts">
    import NostrNoteActions from "$lib/components/NostrNoteActions.svelte";
    import {formatTimestamp} from '$lib/nostr/utils';
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg?url";

    export let message;
    export let pool;
</script>

<div class="flex py-2" class:mt-0={message.samePubKey} class:mt-5={!message.samePubKey} class:profileInfo={!message.samePubKey} data-note-id="{message.id}">

    <!-- AVATAR -->
    <div class="mr-4">
        <div class="chat-image avatar">
            <div class="w-8 ml-2 rounded-full ring-primary ring-offset-base-100 ring-offset-1" class:ring={!message.samePubKey}>
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
                <div class="chat-header lg:flex items-center space-y-1 lg:space-x-2">
                    <p class="mr-3" class:profileInfoName={!message.samePubKey}>{message.profileName ?? message.pubkey.slice(0, 8)}</p>
                    {#if message.nip05verified}
                        <div class="lg:flex space-x-2">
                            <div class="badge badge-primary text-xs whitespace-nowrap">NIP-05 verified</div>
                            <div class="badge badge-secondary text-xs whitespace-nowrap">{message.nip05}</div>
                        </div>
                    {/if}
                </div>
            {/if}
            <div class="text-xs opacity-50">{formatTimestamp(message.created_at)}</div>
        </div>

        <div class="">
            <!-- MESSAGES AND ICONS -->
            <div class="chat-bubble my-4">{@html message.content}</div>
            <NostrNoteActions {pool} {message}></NostrNoteActions>
        </div>
    </div>
</div>
