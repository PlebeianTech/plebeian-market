<script lang="ts">
    import NostrNoteActions from "$lib/components/nostr/NoteActions.svelte";
    import NostrReplyNote from "$lib/components/nostr/ReplyNote.svelte";
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
                <div class="chat-header lg:flex items-center">
                    <p class="mr-3" class:profileInfoName={!message.samePubKey}>{message.profileName ?? message.pubkey.slice(0, 8)}</p>
                    {#if message.nip05verified}
                        <div class="dropdown dropdown-bottom dropdown-hover dropdown-end">
                            <label tabindex="0" class="hover:cursor-pointer hover:scale-110 duration-300">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                                    <path fill-rule="evenodd" d="M8.603 3.799A4.49 4.49 0 0112 2.25c1.357 0 2.573.6 3.397 1.549a4.49 4.49 0 013.498 1.307 4.491 4.491 0 011.307 3.497A4.49 4.49 0 0121.75 12a4.49 4.49 0 01-1.549 3.397 4.491 4.491 0 01-1.307 3.497 4.491 4.491 0 01-3.497 1.307A4.49 4.49 0 0112 21.75a4.49 4.49 0 01-3.397-1.549 4.49 4.49 0 01-3.498-1.306 4.491 4.491 0 01-1.307-3.498A4.49 4.49 0 012.25 12c0-1.357.6-2.573 1.549-3.397a4.49 4.49 0 011.307-3.497 4.49 4.49 0 013.497-1.307zm7.007 6.387a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
                                </svg>
                            </label>
                            <ul tabindex="0" class="dropdown-content translate-x-20">
                                <li>
                                    <div class="badge badge-secondary text-xs whitespace-nowrap">{message.nip05}</div>
                                </li>
                            </ul>
                        </div>
                    {/if}
                </div>
            {/if}
            <div class="text-xs opacity-50">{formatTimestamp(message.created_at)}</div>
        </div>

        <div class="">
            <!-- REPLY TO -->
            {#if message.repliedToMessage}
                <div class="card card-compact border border-gray-400/70 shadow-xl my-4">
                    {#if typeof message.repliedToMessage === 'object'}
                        <NostrReplyNote message={message.repliedToMessage}></NostrReplyNote>
                    {:else}
                        <span>Replying to #{message.repliedToMessage.slice(0, 8)}</span>
                    {/if}
                </div>
            {/if}

            <!-- MESSAGES AND ICONS -->
            <div class="my-4">{@html message.content}</div>
            <NostrNoteActions {pool} {message} {onReply}></NostrNoteActions>
        </div>
    </div>
</div>
