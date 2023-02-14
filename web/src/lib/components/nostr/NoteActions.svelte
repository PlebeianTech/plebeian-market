<script lang="ts">
    import {Pool} from "$lib/nostr/pool";
    import {Error} from "$lib/stores";

    export let pool: Pool;
    export let message;
    export let onReply;

    $: reactions = message.reactions;

    let likeCount = 0;
    let dislikeCount = 0;
    let likeIsMine = false;

    $: if (reactions) {
        let likeReactions: Set<string> = reactions.get('+');
        let dislikeReactions = reactions.get('-');

        if (likeReactions) {
            likeCount = likeReactions.size;
            likeIsMine = likeReactions.has(pool.publicKey);
        }
        if (dislikeReactions) {
            dislikeCount = dislikeReactions.size;
        }
    }

    function setReplyToThisEvent(message) {
        if (!pool.writeEnabled) {
            Error.set('You need to either use a Nostr extension for your browser or register into Plebeian Market so we can provide one for you');
            return;
        }

        onReply(message);
        // TODO: scrollToBottom(chatArea);
        document.getElementById('nostrMessageSendText').focus();
    }

    /* Will we support delete functionality?
    async function deleteNote(message) {
        if (await pool.deleteNote(message)) {
            message = null;
            // TODO:
            // we're modifying sortedMessages here, but
            // we need to remove the note from "messages" itself
        }
    }
    */
</script>

<!-- ICONS -->
<div class="flex items-center w-full justify-between mb-2">
    <!-- LIKE -->
    <button class="btn btn-ghost 777tooltip 777tooltip-right" data-tip="like" on:click|preventDefault={() => pool.sendReaction(message, '+')}>
        {#if likeIsMine }
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FF0000" class="w-6 h-6">
                <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
            </svg>
        {:else}
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
            </svg>
        {/if}
        &nbsp;{#if likeCount} {likeCount} {/if}
    </button>

    <!-- OTHER -->
    {#if reactions}
        {#each [...reactions] as [reaction, pubkeys]}
            {#if ['+', '-'].indexOf(reaction) === -1}
                <button class="btn btn-ghost" on:click|preventDefault={() => pool.sendReaction(message, reaction)}>
                    {reaction} {pubkeys.size}
                </button>
            {/if}
        {/each}
    {/if}

    <!-- REPLY -->
    <button class="btn btn-ghost 777tooltip 777tooltip-right" data-tip="reply"  on:click|preventDefault={() => setReplyToThisEvent(message)}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
        </svg>
        &nbsp;{#if message.replies} {message.replies.length} {/if}
    </button>

    <!-- REPOST -->
    <button class="btn btn-ghost tooltip tooltip-right" data-tip="repost">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
        </svg>
    </button>

    <!-- EMBED -->
    <button class="btn btn-ghost tooltip tooltip-left" data-tip="embed">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
        </svg>
    </button>
</div>
