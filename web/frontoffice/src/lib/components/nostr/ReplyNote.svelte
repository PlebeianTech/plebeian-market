<script lang="ts">
    import type { VitaminedMessage } from "$lib/components/nostr/types";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg?url";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";

    export let message: VitaminedMessage;
    export let onReply = (_) => {};
    export let closeButton: boolean = false;

    $: profilePicture = message.profile && message.profile.picture ? message.profile.picture : profilePicturePlaceHolder;
    $: displayName = message.profile && message.profile.name ? message.profile.name : (message.pubkey ? message.pubkey.slice(0, 8) : "");
</script>

<div class="flex my-4">
    {#if closeButton}
        <div class="card-actions justify-end">
            <button class="btn btn-square btn-sm tooltip flex" data-tip="Close reply message" on:click|preventDefault={() => onReply(null)}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
        </div>
    {/if}

    <div>
        <div class="chat-image avatar">
            <div class="w-10 lg:w-12 ml-3 lg:mx-4 mr-0 rounded-full">
                <img src="{profilePicture}" alt="Nostr avatar for {displayName}" class:profileInfoImage={!message.samePubKey} />
            </div>
        </div>
    </div>

    <div class="items-center w-full px-4">
        <div class="chat-header flex items-center">
            <p class="mr-3 space-y-1">{displayName}</p>

            {#if message.nip05VerifiedAddress}
                <Nip05Checkmark address={message.nip05VerifiedAddress} />
            {/if}
        </div>

        {#if message.content}
            <div class="mt-2 text-sm">{@html message.content.substring(0,60)}{#if message.content.length > 60}...{/if}</div>
        {/if}
    </div>
</div>
