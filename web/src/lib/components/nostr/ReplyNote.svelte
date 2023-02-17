<script lang="ts">
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg?url";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";

    export let message;
</script>

<div class="flex my-4">
    <div>
        <div class="chat-image avatar">
            <div class="w-10 lg:w-12 ml-3 lg:mx-4 mr-0 rounded-full">
                <img src="{message.profileImage ?? profilePicturePlaceHolder}" alt="profile picture" class:profileInfoImage={!message.samePubKey} />
            </div>
        </div>
    </div>

    <div class="items-center w-full px-4">
        <div class="chat-header flex items-center">
            <p class="mr-3 space-y-1">{message.profileName ?? message.pubkey.slice(0, 8)}</p>

            {#if message.nip05}
                <Nip05Checkmark {message}></Nip05Checkmark>
            {/if}
        </div>

        <div class="mt-2 text-sm">{@html message.content.substring(0,60)}{#if message.content.length > 60}...{/if}</div>
    </div>
</div>
