<script lang="ts">
    import NostrNote from "$lib/components/nostr/Note.svelte";
    import NostrReplyNote from "$lib/components/nostr/ReplyNote.svelte";
    import {onDestroy, onMount, beforeUpdate, afterUpdate} from "svelte";
    import {token, user, Error} from "$lib/stores";
    import {Event, Sub, Filter, generatePrivateKey, Kind} from "nostr-tools";
    import {Pool} from "$lib/nostr/pool";
    import {hasExtension, queryNip05, filterTags, getMessage, localStorageNostrPreferPMId} from '$lib/nostr/utils';
    import {ErrorHandler, putProfile} from "$lib/services/api";
    import {requestLoginModal} from "$lib/utils";

    export let nostrRoomId: string;
    export let messageLimit: number = 60;
    export let messagesSince: number = 1672837281;  // January 4th 2023
    export let fixedChatBox: boolean = false;   // Makes the chatbox fixed to the bottom of the screen
    export let onReply = (message) => {nostrEventBeingRepliedTo = message};

    let nostrEventBeingRepliedTo = null;
    let nostrPreferenceCheckboxChecked;
    let textarea;
    let nostrExtensionEnabled: boolean;
    let messages = [];
    let sortedMessages = [];
    let autoscroll: Boolean = true;
    let ignoreNextScrollEvent = false;

    const nostrQueriesBatchSize = 100;
    const nostrOrderMessagesDelay = 1500;
    const nostrBackgroundJobsDelay = 3000;
    const nostrMediaCacheEnabled = false;

    let orderMessagesTimer = null;
    let backgroundJobsTimer = null;

    type UserProfile = {
        name: string;
        about: string;
        picture: string;
        nip05: string;
    };

    // null: to be requested
    // true: requested
    // UserProfile: the user profile
    let profileImagesMap = new Map<string, null | true | UserProfile>();

    // null: to be requested
    // true: requested
    // false: the request errored out (so don't ask again)
    // other: the public key of the user as specified in the nip05 registry
    let nip05 = new Map<string, null | boolean | string>();

    // null: to be requested
    // true: requested
    let notesMap = new Map();

    const pool: Pool = new Pool();

    function orderAndVitamineMessages() {
        let lastMessagePublicKey = null

        sortedMessages = messages
            .sort((a, b) => {
                return a.created_at >= b.created_at
                    ? 1
                    : -1
            })
            .map(function(message) {
                if (lastMessagePublicKey === message.pubkey) {
                    message.samePubKey = true
                }

                const profileInfo: null | true | UserProfile = profileImagesMap.get(message.pubkey)

                // Profile info / nip-05 verification
                if (profileInfo !== null && profileInfo !== true) {
                    if (profileInfo.picture) {
                        if (nostrMediaCacheEnabled) {
                            message.profileImage = 'https://media.nostr.band/thumbs/' + message.pubkey.slice(-4) + '/' + message.pubkey + '-picture-64';
                        } else {
                            message.profileImage = profileInfo.picture
                        }
                    }

                    if (profileInfo.name) {
                        message.profileName = profileInfo.name
                    }

                    if (profileInfo.about) {
                        message.profileAbout = profileInfo.about
                    }

                    if (profileInfo.nip05) {
                        let nip05verificationPublicKey = nip05.get(profileInfo.nip05);

                        if (nip05verificationPublicKey === undefined) {
                            nip05.set(profileInfo.nip05, null);
                        } else if (nip05verificationPublicKey !== null) {
                            if (message.pubkey === nip05verificationPublicKey) {
                                let nip05Address = profileInfo.nip05;

                                if (nip05Address.startsWith('_@')) {
                                    message.nip05 = nip05Address.substring(2);
                                } else {
                                    message.nip05 = nip05Address;
                                }
                            }
                        }
                    }
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

    function addMessageIfDoesntExist(newMessage: Event) {
        for (const message of messages) {
            if (message.id === newMessage.id) {
                return;
            }
        }

        messages.push(newMessage);

        saveProfilePubkey(newMessage.pubkey);
        saveNoteId(newMessage.id);
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
        let profilesToGetLocal = [];

        let i=0;

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

        if (profilesToGetLocal.length === 0) {
            return;
        }

        pool.relays.forEach(relay => {
            const sub: Sub = relay.sub([{
                kinds: [Kind.Metadata],
                authors: profilesToGetLocal
            }]);
            sub.on('event', event => {
                const profileContentJSON = event.content;
                const pubKey = event.pubkey;

                if (profileContentJSON) {
                    profileImagesMap.set(pubKey, JSON.parse(profileContentJSON));
                }
            });

            pool.subscriptions.push(sub);
        })
    }

    function queryNoteInformationInBatches() {
        let noteInfoToGetLocal: string[] = [];

        let i=0;

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

        pool.relays.forEach(relay => {
            let filter: Filter = {
                kinds: [
                    Kind.Text,
                    Kind.Reaction
                ],
                '#e': noteInfoToGetLocal
            };

            const sub: Sub = relay.sub([filter]);

            sub.on('event', event => {
                const kind = event.kind;

                // TODO: REPLIES AND LIKES

                if (kind === Kind.Reaction) {
                    const id = event.tags.reverse().find((tag: any) => tag[0] === 'e')?.[1]; // last e tag is the liked post
                    const eventReaction: string = event.content;
                    const eventPubkey: string = event.pubkey;

                    if (!id) {
                        console.error('EVENT WITHOUT ID !!!');
                        return;
                    }

                    for (let message of messages) {
                        if (message.id === id) {
                            let reactions: Map<string, Set<string>> | undefined = message.reactions;
                            if (reactions === undefined) {
                                reactions = new Map();
                                message.reactions = reactions;
                            }

                            let reaction: Set<string> = reactions.get(eventReaction);
                            if (reaction === undefined) {
                                reaction = new Set();
                                reactions.set(eventReaction, reaction);
                            }
                            reaction.add(eventPubkey);

                            break;
                        }
                    }
                }
            });

            pool.subscriptions.push(sub);
        })
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

    function updateBrowserExtensionCheckbox() {
        let extensionCheckBox = <HTMLInputElement>document.getElementById('use_browser_extension');
        if (!extensionCheckBox) {
            console.error('No browser extension checkbox found');
            return;
        }

        if (nostrExtensionEnabled) {
            nostrPreferenceCheckboxChecked = localStorage.getItem(localStorageNostrPreferPMId) === null;
            extensionCheckBox.disabled = false;
            extensionCheckBox.classList.remove("tooltip");
            extensionCheckBox.classList.remove("cursor-help");
        } else {
            nostrPreferenceCheckboxChecked = false;
        }
    }

    async function onChangeNostrPreferenceCheckbox(changeEvent) {
        if (changeEvent.target.checked) {
            localStorage.removeItem(localStorageNostrPreferPMId);
        } else {
            localStorage.setItem(localStorageNostrPreferPMId, '1');
        }

        await pool.setPoolPublicKey();
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

    $: if (nostrExtensionEnabled || ($token && $user)) {
        pool.writeEnabled = true;
    }

    onMount(async () => {
        nostrExtensionEnabled = hasExtension();

        await pool.setPoolPublicKey();

        updateBrowserExtensionCheckbox();

        if (nostrRoomId !== null) {
            pool.connectAndSubscribeToChannel({
                nostrRoomId,
                messageLimit,
                messagesSince,
                'callbackFunction': addMessageIfDoesntExist
            });
        } else {
            console.error('Chat.svelte:onMount - We must have the nostrRoomId at this point');
        }

        processMessagesPeriodically();
        doBackgroundJobsPeriodically()

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

            pool.user = $user;
        }
    );

    onDestroy(async () => {
        userUnsubscribe();
        await pool.unsubscribeEverything();
        await pool.disconnect();

        clearTimeout(orderMessagesTimer);
        clearTimeout(backgroundJobsTimer);
    })

    const onKeyPress = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    const sendMessage = async () => {
        const content = textarea.value.trim();

        if (!pool.writeEnabled) {
            Error.set('You need to either use a Nostr extension for your browser or register into Plebeian Market so we can provide one for you');
        } else if (content) {
            if (await pool.sendMessage(null, content, nostrRoomId, nostrEventBeingRepliedTo)) {
                nostrEventBeingRepliedTo = null;
                textarea.value = '';
                scrollToBottom();
            }
        }
    }

    const scrollToBottom = () => {
        ignoreNextScrollEvent = true;
        window.scrollTo(0, document.body.scrollHeight);
    }

    afterUpdate(() => {
        if (autoscroll) {
            scrollToBottom()
        }
    })
</script>

<!-- BROWSER EXTENSION -->
<div class="w-full bg-dark lg:flex items-center hidden lg:block">
    <div class="flex justify-start">
        <label class="cursor-pointer label">
            <input id="use_browser_extension" type="checkbox" class="toggle toggle-primary mr-2 tooltip cursor-help" data-tip="Nostr browser extension not present"
                   bind:checked={nostrPreferenceCheckboxChecked}
                   on:change={e => {onChangeNostrPreferenceCheckbox(e)}}
                   disabled />
            <span class="label-text">Use browser extension's identity</span>
        </label>
    </div>
</div>

<!-- BROWSER EXTENSION INFO -->
<div class="flex flex-col hidden lg:grid">
    {#if nostrPreferenceCheckboxChecked}
        <small>You'll sign messages with your extension when you write in the channel.</small>
    {:else}
        {#if $token && $user}
            <small>You're using your Plebeian Market generated Nostr identity. It's recommended to install a Nostr browser extension
                (<a class="link" href="https://github.com/fiatjaf/nos2x" target="_blank" rel="noreferrer">nos2x</a>,
                <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a> or
                <a class="link" href="https://www.blockcore.net/wallet" target="_blank" rel="noreferrer">Blockcore</a>) so you use
                your own Nostr identity.
            </small>
        {:else}
            <small>You need to install a Nostr browser extension (this is the recommended way: try <a class="link" href="https://github.com/fiatjaf/nos2x" target="_blank" rel="noreferrer">nos2x</a>,
                <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a> or
                <a class="link" href="https://www.blockcore.net/wallet" target="_blank" rel="noreferrer">Blockcore</a>) or
                <a class="font-bold text-center cursor-pointer" on:click={requestLoginModal} on:keypress={requestLoginModal}>Login</a>
                into Plebeian Market to be able to publish messages.
            </small>
        {/if}
    {/if}
</div>

<div tabindex="0" class="mt-3 collapse collapse-plus border border-gray-400/70 bg-base-100 rounded-box mb-4 hidden lg:grid">
    <input type="checkbox" />
    <div class="collapse-title text-l font-medium">
        We use <b>Nostr</b> to power this chat. Click here to see more info
    </div>
    <div class="collapse-content">
        <p class="mb-4">If you prefer to participate in this chat using another Nostr client, you'll need one that support channels and introduce this channel ID: {nostrRoomId}</p>
    </div>
</div>

<div class="flex flex-col mt-2 mb-6 pb-6 bg-cover bg-top bg-info-content-200 items-center justify-center gap-2 overflow-x-hidden overflow-y-hidden w-full"
     style="background-size: 5px 5px; background-image: radial-gradient(hsla(var(--bc)/.2) 0.5px,hsla(var(--b2)/1) 0.5px);">
   <div>
        {#each sortedMessages as message}
            <NostrNote {pool} {message} {onReply}></NostrNote>
        {/each}
   </div>
</div>

<div class="grid grid-cols-2 p-3 bg-black rounded-lg items-center inset-x-0 bottom-0 mx-auto w-screen lg:w-2/3" class:fixed={fixedChatBox}>
    {#if nostrEventBeingRepliedTo !== null}
        <div class="col-span-2">
            <NostrReplyNote message={nostrEventBeingRepliedTo} closeButton={true} {onReply}></NostrReplyNote>
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

        <div on:click={sendMessage}
             class="p-4 flex justify-center hover:scale-110 duration-300 transition-all cursor-pointer text-white">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
        </div>
    </div>
</div>
