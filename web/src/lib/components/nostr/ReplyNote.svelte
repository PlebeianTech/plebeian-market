<script lang="ts">
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg?url";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";

    export let message;
</script>

<div class="flex mt-5">
    <!-- AVATAR -->
    <div>
        <div class="chat-image avatar">
            <div class="w-14 mx-4 mr-0 rounded-full ring-primary ring-offset-base-100 ring-offset-1" class:ring={!message.samePubKey}>
                <img src="{message.profileImage ?? profilePicturePlaceHolder}" alt="profile picture" class:profileInfoImage={!message.samePubKey} />
            </div>
        </div>
    </div>

    <div class="items-center w-full px-4">
        <!-- NAME, BADGES, DATE -->
        <div class="space-y-1">
            <div class="chat-header lg:flex items-center space-y-1 lg:space-x-2">
                <p class="mr-3">{message.profileName ?? message.pubkey.slice(0, 8)}</p>

                {#if message.nip05verified}
                    <Nip05Checkmark {message}></Nip05Checkmark>
                {/if}
            </div>
        </div>

        <div class="">
            <!-- MESSAGES AND ICONS -->
            <div class="my-4">{@html message.content.substring(0,60)}{#if message.content.length > 60}...{/if}</div>
        </div>
    </div>
</div>
