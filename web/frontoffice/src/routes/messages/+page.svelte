<script>
    import {NostrPool, NostrPublicKey, privateMessages} from "$lib/stores";
    import {onMount} from "svelte";
    import {checkExtensionOrShowDialog, sendMessage} from "$lib/services/nostr";
    import {nip19} from "nostr-tools";
    import SimpleNote from "$lib/components/nostr/SimpleNote.svelte";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    let selectedConversationPubkey = null;

    let sortedMessages = [];
    let chatTextarea;

    export let onImgError = (imgElement) => {
        imgElement.onerror = "";
        imgElement.src = profilePicturePlaceHolder;
    }

    onMount(async () => {
        if (!$NostrPublicKey) {
            if (checkExtensionOrShowDialog()) {
                $NostrPublicKey = await window.nostr.getPublicKey();
            }
        }
    });

    $: {
        if ($privateMessages.human && $privateMessages.human[selectedConversationPubkey]) {
            sortedMessages = Object.entries($privateMessages.human[selectedConversationPubkey]).sort((a, b) => {
                return a[1].created_at - b[1].created_at;
            });
        } else {
            sortedMessages = [];
        }
    }

    const onKeyPress = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    }

    async function send() {
        const content = textarea.value.trim();

        if ($NostrPublicKey === null) {
            ErrorStore.set("You need to use a Nostr browser extension to be able to send messages to the chat.");
        } else if (content) {
            await sendMessage($NostrPool, content, nostrRoomId, nostrEventBeingRepliedTo,
                () => {
                    //nostrEventBeingRepliedTo = null;
                    textarea.value = '';
//                    scrollToBottom();
                });
        }
    }
</script>

<svelte:head>
    <title>Messages</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-8 lg:mb-8 p-4">Messages</h1>

<div class="flex lg:px-6 h-[46rem]">

    <div class="menu card h-auto max-h-full mb-6 gap-2 rounded-box place-items-center w-1/3 p-1 bg-cover bg-top bg-base-300 bg-info-content-200 overflow-y-auto overflow-x-hidden">
        <ul class="p-1">
            {#each Object.entries($privateMessages.human ?? []) as [privateKey, message]}
                <li class="rounded-lg"
                    class:bg-primary={selectedConversationPubkey === privateKey}
                    on:click={() => selectedConversationPubkey = privateKey}
                >
                    <a>
                        <div class="avatar">
                            <div class="w-16 rounded-full">
                                <img src="{message.picture ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
                            </div>
                        </div>
                        {message.name ?? nip19.npubEncode(privateKey)}
                    </a>
                </li>
            {/each}
            {#each Object.entries($privateMessages.human ?? []) as [privateKey, message]}
                <li class="rounded-lg"
                    class:bg-primary={selectedConversationPubkey === privateKey}
                    on:click={() => selectedConversationPubkey = privateKey}
                >
                    <a>
                        <div class="avatar">
                            <div class="w-16 rounded-full">
                                <img src="{message.picture ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
                            </div>
                        </div>
                        {message.name ?? nip19.npubEncode(privateKey)}
                    </a>
                </li>
            {/each}
        </ul>
    </div>

    <div class="divider lg:divider-horizontal"></div>

    <div class="flex flex-col flex-grow w-full mb-6 p-4 gap-2 card bg-base-300 rounded-box bg-cover bg-top bg-info-content-200 overflow-x-hidden overflow-y-auto"
         style="background-size: 5px 5px; background-image: radial-gradient(hsla(var(--bc)/.2) 0.5px,hsla(var(--b2)/1) 0.5px);">
        <div class="flex-none min-w-full px-4 sm:px-6 md:px-0 overflow-hidden lg:overflow-auto scrollbar:!w-1.5 scrollbar:!h-1.5 scrollbar:bg-transparent scrollbar-track:!bg-slate-100 scrollbar-thumb:!rounded scrollbar-thumb:!bg-slate-300 scrollbar-track:!rounded dark:scrollbar-track:!bg-slate-500/[0.16] dark:scrollbar-thumb:!bg-slate-500/50 lg:supports-scrollbars:pr-2">
            {#if selectedConversationPubkey}
                {#each sortedMessages as [publicKey, message]}
                    {#if typeof message === 'object'}
                        <SimpleNote {message} />
                    {/if}
                {/each}

                {#each sortedMessages as [publicKey, message]}
                    {#if typeof message === 'object'}
                        <SimpleNote {message} />
                    {/if}
                {/each}

                {#if selectedConversationPubkey}
                    <div class="grid grid-cols-2 p-3 bg-black rounded-lg items-center inset-x-0 bottom-0 mx-auto w-screen lg:w-2/3 mt-8">
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
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                                </svg>
                            </div>
                        </div>
                    </div>
                {/if}
            {:else}
                <p class="mt-6">Choose a conversation to see the messages.</p>
            {/if}
        </div>
    </div>
</div>
