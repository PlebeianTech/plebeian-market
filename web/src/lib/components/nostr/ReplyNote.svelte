<script lang="ts">
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg?url";

    export let message;
</script>

<div class="flex" class:mt-0={message.samePubKey} class:mt-5={!message.samePubKey}>
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

    <div class="items-center w-full px-4">
        <!-- NAME, BADGES, DATE -->
        <div class="space-y-1">
            {#if !message.samePubKey}
                <div class="chat-header lg:flex items-center space-y-1 lg:space-x-2">
                    <p class="mr-3" class:profileInfoName={!message.samePubKey}>{message.profileName ?? message.pubkey.slice(0, 8)}</p>
                </div>
            {/if}
        </div>

        <div class="">
            <!-- MESSAGES AND ICONS -->
            <div class="chat-bubble my-4">{@html message.content.substring(0,60)}</div>
        </div>
    </div>
</div>
