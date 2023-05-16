<script>
    import {NostrPool, NostrPublicKey, privateMessages} from "$lib/stores";
    import {onMount} from "svelte";
    import {checkExtensionOrShowDialog, sendPrivateMessage} from "$lib/services/nostr";
    import {nip19} from "nostr-tools";
    import SimpleNote from "$lib/components/nostr/SimpleNote.svelte";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";
    import SendMessage from "$sharedLib/components/icons/SendMessage.svelte";
    import { page } from '$app/stores'
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";

    let selectedConversationPubkey = null;
    let sortedConversations;
    let sortedMessages = [];
    let chatTextarea;
    let newConversationPubkey;

    // Messages
    $: {
        if (selectedConversationPubkey && $privateMessages.human && $privateMessages.human[selectedConversationPubkey]) {
            sortedMessages = Object.entries($privateMessages.human[selectedConversationPubkey].messages).sort((a, b) => {
                return a[1].created_at - b[1].created_at;
            });

            scrollToBottom();

            const maxTimestampConversation = $privateMessages.human[selectedConversationPubkey].maxTimestamp;
            let messagesStorage = localStorage.getItem('readMessages');
            let messages = JSON.parse(messagesStorage) ?? {};

            if (maxTimestampConversation > (messages[selectedConversationPubkey] ?? 0)) {
                messages[selectedConversationPubkey] = maxTimestampConversation;

                localStorage.setItem('readMessages', JSON.stringify(messages));

                // Fire private messages reactivity manually
                $privateMessages.human[selectedConversationPubkey].maxTimestamp = $privateMessages.human[selectedConversationPubkey].maxTimestamp;
            }
        } else {
            sortedMessages = [];
        }
    }

    // Conversations
    $: {
        if ($privateMessages.human) {
            sortedConversations = Object.entries($privateMessages.human).sort((a, b) => {
                return b[1].maxTimestamp - a[1].maxTimestamp;
            });
        } else {
            sortedConversations = [];
        }
    }

    const onKeyPress = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    }

    async function send() {
        const content = chatTextarea.value.trim();

        await sendPrivateMessage($NostrPool, selectedConversationPubkey, content,
            async (relay) => {
                chatTextarea.value = '';
                console.log('-------- Private message accepted by relay:', relay);
            }
        );
    }

    function selectConversation(publicKey) {
        if (!publicKey) {
            return;
        }

        selectedConversationPubkey = publicKey;
    }

    async function scrollToBottom() {
        await new Promise(resolve => setTimeout(resolve, 150));

        let chatScrollableDiv = document.getElementById("conversationMessages");
        if (chatScrollableDiv !== null) {
            chatScrollableDiv.scrollTop = chatScrollableDiv.scrollHeight;
        }
    }

    export let onImgError = (imgElement) => {
        imgElement.onerror = "";
        imgElement.src = profilePicturePlaceHolder;
    }

    onMount(async () => {
        // localStorage.removeItem('readMessages');

        if (!$NostrPublicKey) {
            if (checkExtensionOrShowDialog()) {
                $NostrPublicKey = await window.nostr.getPublicKey();
            }
        }

        const newMessagePubKey = $page.url.searchParams.get('newMessagePubKey');

        if (newMessagePubKey && newMessagePubKey.length === 64) {
            newConversationPubkey = newMessagePubKey;
            selectConversation(newMessagePubKey);
        }
    });
</script>

<svelte:head>
    <title>Private Messages</title>
</svelte:head>

<Titleh1>Private Messages</Titleh1>

<div class="flex h-[46rem]">
    <div class="w-1/3 menu card h-auto max-h-full gap-2 rounded-box p-1 bg-cover bg-top bg-base-300 bg-info-content-200 overflow-y-auto overflow-x-hidden      scrollbar:!w-1.5 scrollbar:!h-1.5 scrollbar:bg-transparent scrollbar-track:!bg-slate-100 scrollbar-thumb:!rounded scrollbar-thumb:!bg-slate-300 scrollbar-track:!rounded dark:scrollbar-track:!bg-slate-500/[0.16] dark:scrollbar-thumb:!bg-slate-500/50 lg:supports-scrollbars:pr-2 hover:scrollbar-thumb:!bg-slate-400/80">
        {#if newConversationPubkey && !$privateMessages.human[newConversationPubkey]}
            <li class="rounded-lg w-full"
                class:bg-primary={selectedConversationPubkey === newConversationPubkey}
                on:click={() => selectConversation(newConversationPubkey)}
            >
                <div>
                    <div class="avatar indicator">
                        <div class="w-16 rounded-full">
                            <img src="{profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
                        </div>
                    </div>
                    New conversation: {nip19.npubEncode(newConversationPubkey)}
                </div>
            </li>
        {/if}

        {#each sortedConversations as [privateKey, conversation]}
            <li class="rounded-lg w-full"
                class:bg-primary={selectedConversationPubkey === privateKey}
                on:click={() => selectConversation(privateKey)}
            >
                <div class="w-full">
                    <div class="avatar indicator">
                        {#if conversation.unreadMessages}
                            <span class="indicator-item badge badge-sm badge-error">
                                {conversation.unreadMessages}
                            </span>
                        {/if}
                        <div class="w-16 rounded-full">
                            <img src="{conversation.picture ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
                        </div>
                    </div>
                    {conversation.name ?? nip19.npubEncode(privateKey)}
                </div>
            </li>
        {/each}
    </div>

    <div class="divider lg:divider-horizontal"></div>

    <div class="flex flex-col flex-grow w-full p-4 gap-2 card bg-base-300 rounded-box bg-cover bg-top bg-info-content-200 overflow-x-hidden overflow-y-auto            scrollbar:!w-1.5 scrollbar:!h-1.5 scrollbar:bg-transparent scrollbar-track:!bg-slate-100 scrollbar-thumb:!rounded scrollbar-thumb:!bg-slate-300 scrollbar-track:!rounded dark:scrollbar-track:!bg-slate-500/[0.16] dark:scrollbar-thumb:!bg-slate-500/50 lg:supports-scrollbars:pr-2 hover:scrollbar-thumb:!bg-slate-400/80"
         id="conversationMessages" style="background-size: 5px 5px; background-image: radial-gradient(hsla(var(--bc)/.2) 0.5px,hsla(var(--b2)/1) 0.5px);">
        {#if selectedConversationPubkey}
            {#each sortedMessages as [publicKey, message]}
                {#if typeof message === 'object'}
                    <SimpleNote {message} />
                {/if}
            {/each}

            <div class="grid grid-cols-2 w-screen lg:w-2/3 mt-8 p-3 bg-black rounded-lg items-center inset-x-0 bottom-0 mx-auto">
                <div class="flex col-span-2">
                    <textarea
                            rows="1"
                            id="nostrMessageSendText"
                            autofocus
                            placeholder="Type your message"
                            bind:this={chatTextarea}
                            on:keypress={onKeyPress}
                            class="p-2 w-full bg-medium placeholder:text-light outline-0 resize-none"></textarea>

                    <div on:click={send} on:keypress={onKeyPress}
                         class="p-4 flex justify-center hover:scale-110 duration-300 transition-all cursor-pointer text-white">
                        <div class="w-6 h-6"><SendMessage /></div>
                    </div>
                </div>
            </div>
        {:else}
            <p class="m-6">Choose a conversation to see the messages.</p>
        {/if}
    </div>
</div>
