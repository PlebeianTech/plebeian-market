<script lang="ts">
    import { onDestroy, onMount, afterUpdate } from 'svelte';
    import { type Event, generatePrivateKey, Kind } from 'nostr-tools';
    import type { VitaminedMessage } from "$lib/components/nostr/types";
    import NostrNote from "$lib/components/nostr/Note.svelte";
    import NostrReplyNote from "$lib/components/nostr/ReplyNote.svelte";
    import { hasExtension, queryNip05, filterTags, localStorageNostrPreferPMId, setPublicKey } from "$lib/nostr/utils";
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { type UserMetadata, subscribeMetadata, subscribeReactions, subscribeChannel, sendMessage } from "$lib/services/nostr";
    import { token, user, NostrPool, NostrPublicKey, Error as ErrorStore, Info as InfoStore } from "$lib/stores";
    import { requestLoginModal } from "$lib/utils";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";
    import SendMessage from "$sharedLibComponents/icons/SendMessage.svelte";

    const USE_MEDIA_CACHE = true;

    export let nostrRoomId: string;
    export let messageLimit: number = 60;
    export let messagesSince: number = 1672837281;  // January 4th 2023
    export let fixedChatBox: boolean = false;   // Makes the chatbox fixed to the bottom of the screen
    export let onReply = (message) => {nostrEventBeingRepliedTo = message};

    let nostrEventBeingRepliedTo = null;
    let textarea;
    let nostrExtensionEnabled: boolean;
    let messages: VitaminedMessage[] = [];
    let sortedMessages: VitaminedMessage[] = [];
    let autoscroll: Boolean = true;
    let ignoreNextScrollEvent = false;

    function getMessage(messages: VitaminedMessage[], messageId) {
        for (const message of messages) {
            if (message.id === messageId) {
                return message;
            }
        }
    }

    const nostrQueriesBatchSize = 100;
    const nostrOrderMessagesDelay = 1500;
    const nostrBackgroundJobsDelay = 3000;

    let orderMessagesTimer: ReturnType<typeof setTimeout> | null = null;
    let backgroundJobsTimer: ReturnType<typeof setTimeout> | null = null;

    // null: to be requested
    // true: requested
    // UserProfile: the user profile
    let profileImagesMap = new Map<string, null | true | UserMetadata>();

    // null: to be requested
    // true: requested
    // false: the request errored out (so don't ask again)
    // other: the public key of the user as specified in the nip05 registry
    let nip05 = new Map<string, null | boolean | string>();

    // null: to be requested
    // true: requested
    let notesMap = new Map();

    export let onImgError = (imgElement, message) => {
        imgElement.onerror = "";
        imgElement.src = profilePicturePlaceHolder;

        // If the image is broken, let's put the placeholder image
        // in the profile so the next re-draws of the note does not
        // try to put the broken image again
        let profileInfo = profileImagesMap.get(message.pubkey)
        if (profileInfo && profileInfo !== null && profileInfo !== true) {
            profileInfo.picture = profilePicturePlaceHolder;
        }
    }

    function orderAndVitamineMessages() {
        let lastMessagePublicKey: string | null = null

        sortedMessages = messages
            .sort((a, b) => a.created_at >= b.created_at ? 1 : -1)
            .map(function(message) {
                if (lastMessagePublicKey === message.pubkey) {
                    message.samePubKey = true;
                }

                const profileInfo: null | true | UserMetadata = profileImagesMap.get(message.pubkey) || null;

                if (profileInfo !== null && profileInfo !== true) {
                    if (profileInfo.picture && USE_MEDIA_CACHE) {
                        profileInfo.picture = `https://media.nostr.band/thumbs/${message.pubkey.slice(-4)}/${message.pubkey}-picture-64`;
                    }

                    if (profileInfo.nip05) {
                        let nip05verificationPublicKey = nip05.get(profileInfo.nip05);

                        if (nip05verificationPublicKey === undefined) {
                            nip05.set(profileInfo.nip05, null);
                        } else if (nip05verificationPublicKey !== null) {
                            if (message.pubkey === nip05verificationPublicKey) {
                                let nip05Address = profileInfo.nip05;

                                if (nip05Address.startsWith('_@')) {
                                    message.nip05VerifiedAddress = nip05Address.substring(2);
                                } else {
                                    message.nip05VerifiedAddress = nip05Address;
                                }
                            }
                        }
                    }

                    message.profile = profileInfo;
                }

                // Tags for message type
                filterTags(message.tags, 'e').forEach(tag => {
                    const id = tag[1];

                    if (id !== nostrRoomId) {
                        let repliedToMessage = getMessage(messages, id);
                        if (repliedToMessage !== undefined) {
                            // Adding the reply id of the message to the replied message
                            let replies: Array<string> = repliedToMessage.replies || [];

                            if (!replies.includes(message.id)) {
                                replies.push(message.id);
                            }

                            repliedToMessage.replies = replies;

                            // Adding the replied message so we can show it alongside the message
                            message.repliedToMessage = repliedToMessage;
                        } else {
                            // If we don't have the message we're replying to (yet?), we show
                            // that this is a reply to a message #id
                            message.repliedToMessage = id;
                        }
                    }
                });

                // Image preview
                const match = message.content.match(/(https?:\/\/.*\.(?:png|jpg|jpeg|gif|svg))/i);
                const url = match ? match[1] : null;
                if (url !== null) {
                    message.imagePreviewUrl = url;
                }

                lastMessagePublicKey = message.pubkey;

                return message;
            });
    }

    function saveProfilePubkey(pubKey) {
        if (!profileImagesMap.has(pubKey)) {
            profileImagesMap.set(pubKey, null);
        }
    }

    function saveNoteId(noteId) {
        if (!notesMap.has(noteId)) {
            notesMap.set(noteId, null);
        }
    }

    function queryProfilesToNostrRelaysInBatches() {
        let profilesToGetLocal: string[] = [];

        let i = 0;

        for (const [key, profile] of profileImagesMap) {
            if (profile === null) {
                profileImagesMap.set(key, true);
                profilesToGetLocal.push(key);
                i++;

                if (i == nostrQueriesBatchSize) {
                    break;
                }
            }
        }

        if (profilesToGetLocal.length !== 0) {
            subscribeMetadata($NostrPool, profilesToGetLocal, (pk, m) => { profileImagesMap[pk] = m; });
        }
    }

    function queryNoteInformationInBatches() {
        let noteInfoToGetLocal: string[] = [];

        let i = 0;

        for (const [key, note] of notesMap) {
            if (note === null) {
                notesMap.set(key, true);
                noteInfoToGetLocal.push(key);
                i++;

                if (i == nostrQueriesBatchSize) {
                    break;
                }
            }
        }

        if (noteInfoToGetLocal.length === 0) {
            return;
        }

        subscribeReactions($NostrPool, noteInfoToGetLocal,
            (event) => {
                if (event.kind === Kind.Reaction) {
                    const likedEventId = event.tags.reverse().find((tag: any) => tag[0] === 'e')?.[1]; // last e tag is the liked post
                    if (!likedEventId) {
                        return;
                    }
                    const eventReaction: string = event.content;
                    const eventPubkey: string = event.pubkey;

                    for (const message of messages) {
                        if (message.id === likedEventId) {
                            if (message.reactions === undefined) {
                                message.reactions = new Map();
                            }

                            if (message.reactions.get(eventReaction) === undefined) {
                                message.reactions[eventReaction] = new Set();
                            }
                            message.reactions[eventReaction].add(eventPubkey);

                            break;
                        }
                    }
                }
            });
    }

    function queryNip05ServersForVerification() {
        nip05.forEach(async (value, key) => {
            if (value === null) {
                nip05.set(key, true);
                let nip05verificationResult = await queryNip05(key);
                nip05.set(key, nip05verificationResult);
            }
        });
    }

    async function onChangeNostrPreferenceCheckbox(changeEvent) {
        if (changeEvent.target.checked) {
            localStorage.removeItem(localStorageNostrPreferPMId);
        } else {
            localStorage.setItem(localStorageNostrPreferPMId, '1');
        }

        if (await setPublicKey($user)) {
            InfoStore.set("Using the key from your Nostr extension");
        } else {
            ErrorStore.set("Error getting the Nostr public key.");
        }
    }

    function processMessagesPeriodically() {
        orderAndVitamineMessages();
        orderMessagesTimer = setTimeout(processMessagesPeriodically, nostrOrderMessagesDelay);
    }

    function doBackgroundJobsPeriodically() {
        queryProfilesToNostrRelaysInBatches();
        queryNoteInformationInBatches();
        queryNip05ServersForVerification();
        backgroundJobsTimer = setTimeout(doBackgroundJobsPeriodically, nostrBackgroundJobsDelay);
    }

    onMount(async () => {
        nostrExtensionEnabled = hasExtension();

        subscribeChannel($NostrPool, nostrRoomId, messageLimit, messagesSince,
            (newMessage) => {
                for (const message of messages) {
                    if (message.id === newMessage.id) {
                        return;
                    }
                }

                messages.push(newMessage);

                saveProfilePubkey(newMessage.pubkey);
                saveNoteId(newMessage.id);
            });

        processMessagesPeriodically();
        doBackgroundJobsPeriodically();

        window.addEventListener("scroll", function () {
            if (ignoreNextScrollEvent) {
                // Ignore this event because it was done programmatically
                ignoreNextScrollEvent = false;
                return;
            }

            // The user scrolled, so stop auto-scroll
            autoscroll = false;
        });
    });

    const userUnsubscribe = user.subscribe(
        () => {
            if ($user && $user.nostr_private_key === null) {
                let nostr_private_key = generatePrivateKey();

                putProfile($token, {nostr_private_key},
                    u => {
                        user.set(u);
                        console.debug('   ** Nostr: keys saved into user', u)
                    },
                    new ErrorHandler(true)
                );
            }
        }
    );

    onDestroy(async () => {
        userUnsubscribe();
        if (orderMessagesTimer !== null) {
            clearTimeout(orderMessagesTimer);
        }
        if (backgroundJobsTimer !== null) {
            clearTimeout(backgroundJobsTimer);
        }
    })

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
            sendMessage($NostrPool, content, nostrRoomId, nostrEventBeingRepliedTo,
                () => {
                    nostrEventBeingRepliedTo = null;
                    textarea.value = '';
                    scrollToBottom();
                });
        }
    }

    const scrollToBottom = () => {
        ignoreNextScrollEvent = true;

        if (fixedChatBox) {
            window.scrollTo(0, document.body.scrollHeight);
        } else {
            // One div is for mobile scrolling. The other one is for desktop.
            // We need to scroll down both divs for now.
            const chatScrollableDiv = document.getElementById("chatScrollableDiv");
            if (chatScrollableDiv !== null) {
                chatScrollableDiv.scrollTop = chatScrollableDiv.scrollHeight;
            }

            const stallChatContainerDiv = document.getElementById("stallChatContainerDiv");
            if (stallChatContainerDiv !== null) {
                stallChatContainerDiv.scrollTop = stallChatContainerDiv.scrollHeight;
            }
        }
    }

    afterUpdate(() => {
        if (autoscroll) {
            scrollToBottom();
        }
    })
</script>

<!-- BROWSER EXTENSION INFO -->
<div class="flex flex-col hidden lg:grid">
    {#if !nostrExtensionEnabled}
        <small>You need to install a Nostr browser extension (this is the recommended way: try <a class="link" href="https://github.com/fiatjaf/nos2x" target="_blank" rel="noreferrer">nos2x</a>,
            <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a> or
            <a class="link" href="https://www.blockcore.net/wallet" target="_blank" rel="noreferrer">Blockcore</a>) or
            <a href={null} class="font-bold text-center cursor-pointer" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</a>
            into Plebeian Market to be able to publish messages.
        </small>
    {/if}
</div>

<div tabindex="0" class="collapse collapse-plus border border-gray-400/70 bg-base-100 rounded-box mb-4 lg:grid">
    <input type="checkbox" />
    <div class="collapse-title text-l font-medium">We use <b>Nostr</b> to power this chat. Click here to see more info</div>
    <div class="collapse-content">
        <p class="mb-4">If you prefer to participate in this chat using another Nostr client, you'll need one that supports channels and search for this channel ID: {nostrRoomId}</p>
    </div>
</div>

<div class="flex flex-col mt-2 mb-6 pb-6 bg-cover bg-top bg-info-content-200 items-center justify-center gap-2 overflow-x-hidden overflow-y-auto w-full"
     style="background-size: 5px 5px; background-image: radial-gradient(hsla(var(--bc)/.2) 0.5px,hsla(var(--b2)/1) 0.5px);" id="chatScrollableDiv">
    <div>
        {#each sortedMessages as message}
            <NostrNote {message} {onReply} {onImgError} />
        {/each}
    </div>
</div>

<div class="grid grid-cols-2 p-3 bg-black rounded-lg items-center inset-x-0 bottom-0 mx-auto w-screen lg:w-2/3" class:fixed={fixedChatBox}>
    {#if nostrEventBeingRepliedTo !== null}
        <div class="col-span-2">
            <NostrReplyNote message={nostrEventBeingRepliedTo} closeButton={true} {onReply} />
        </div>
    {/if}

    <div class="flex col-span-2">
        <textarea
            rows="1"
            id="nostrMessageSendText"
            autofocus
            placeholder="Type your message"
            bind:this={textarea}
            on:keypress={onKeyPress}
            class="p-2 w-full bg-medium placeholder:text-light outline-0 resize-none"></textarea>

        <div on:click={send} on:keypress={onKeyPress}
             class="p-4 flex justify-center hover:scale-110 duration-300 transition-all cursor-pointer text-white">
            <div class="w-6 h-6"><SendMessage /></div>
        </div>
    </div>
</div>
