<script lang="ts">
    import NostrNote from "$lib/components/nostr/Note.svelte";
    import {onDestroy, onMount, beforeUpdate, afterUpdate} from "svelte";
    import {token, user, nostrEventBeingRepliedTo} from "$lib/stores";
    import Loading from "$lib/components/Loading.svelte";
    import {Event, Sub, Filter, generatePrivateKey, Kind} from "nostr-tools";
    import {Pool} from "$lib/nostr/pool";
    import {hasExtension, queryNip05, wait, localStorageNostrPreferPMId} from '$lib/nostr/utils';
    import {ErrorHandler, putProfile} from "$lib/services/api";

    export let roomData = false;
    export let emptyChatShowsLoading: boolean = false;
    export let nostrRoomId: string;
    export let messageLimit: number = 60;
    export let messagesSince: number = 1672837281;  // January 4th 2023

    const nostrQueriesBatchSize = 100;
    const nostrOrderMessagesDelay = 2000;
    const nostrBackgroundJobsDelay = 4000;
    const nostrMediaCacheEnabled = true;

    let nostrPreferenceCheckboxChecked;

    let textarea;

    let nostrExtensionEnabled;

    let messages = [];
    let sortedMessages = [];
    let chatArea;
    let autoscroll: Boolean = false;

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
                    // No profile picture/name needed
                } else {
                    const profileInfo: null | true | UserProfile = profileImagesMap.get(message.pubkey)

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
                                    message.nip05verified = true;
                                    message.nip05 = profileInfo.nip05;
                                }
                            }
                        }
                    }
                }

                lastMessagePublicKey = message.pubkey

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
        } else {
            nostrPreferenceCheckboxChecked = false;
        }
    }

    function onChangeNostrPreferenceCheckbox(changeEvent) {
        if (changeEvent.target.checked) {
            localStorage.removeItem(localStorageNostrPreferPMId);
        } else {
            localStorage.setItem(localStorageNostrPreferPMId, '1');
        }
    }

    async function updateNostrProfiles() {
        await wait(nostrBackgroundJobsDelay);
        queryProfilesToNostrRelaysInBatches();
        await updateNostrProfiles();
    }

    async function updateNip05Verifications() {
        await wait(nostrBackgroundJobsDelay);
        queryNip05ServersForVerification();
        await updateNip05Verifications();
    }

    async function getNoteInformation() {
        await wait(nostrBackgroundJobsDelay);
        queryNoteInformationInBatches();
        await getNoteInformation();
    }

    async function processMessagesPeriodically() {
        await wait(nostrOrderMessagesDelay);
        orderAndVitamineMessages();
        await processMessagesPeriodically();
    }

    onMount(async () => {
        nostrExtensionEnabled = hasExtension();

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
        updateNostrProfiles();
        updateNip05Verifications();
        getNoteInformation();
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

    onDestroy(() => {
        userUnsubscribe();
        pool.unsubscribeEverything();
        pool.disconnect();
    })

    const onKeyPress = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }

    const sendMessage = async () => {
        const content = textarea.value.trim();

        if (content) {
            if (await pool.sendMessage(null, content, $user, nostrRoomId, $nostrEventBeingRepliedTo)) {
                textarea.value = '';
                scrollToBottom(chatArea);
            }
        }
    }

    // SCROLL TO BOTTOM
    const scrollToBottom = async (node: any) => {
      node.scroll({
        top: node.scrollHeight,
        behavior: 'smooth'
      })
    }

    beforeUpdate(() => {
      autoscroll = chatArea && chatArea.offsetHeight + chatArea.scrollTop > chatArea.scrollHeight - 1
    })

    afterUpdate(() => {
      if(autoscroll) scrollToBottom(chatArea)
    })

</script>

<div>
    {#if roomData !== false}
        <div class="pt-2 md:pt-10 w-full p-4 border-b border-solid border-medium bg-dark flex gap-4">
            <div class="w-14 h-14 rounded-full bg-cover bg-center shrink-0 border border-solid border-white"
                 style="background-image: url('{roomData.picture}')">
            </div>
            <div class="w-full">
                <div class="flex items-center justify-between w-full">
                    <div class="text-lg font-bold">{roomData.name || ''}</div>
                </div>
                <div>{roomData.about || ''}</div>
            </div>
        </div>
    {/if}

    <div class="flex flex-col py-2">
        <div class="mt-4 mb-4 mt:mb-8">
            <div tabindex="0" class="collapse collapse-plus border border-base-300 bg-base-100 rounded-box mb-4">
                <input type="checkbox" />
                <div class="collapse-title text-l font-medium bg-info">
                    We use <b>Nostr</b> to power this chat. Click here to see more info
                </div>
                <div class="collapse-content bg-info">
                    <p class="mb-4">If you prefer to participate in this chat using another Nostr client, you'll need one that support channels and introduce this channel ID: {nostrRoomId}</p>
                </div>
            </div>


            <div class="flex flex-col">
                <div class="form-control w-52">
                    <label class="cursor-pointer label">
                        <input id="use_browser_extension" type="checkbox" class="toggle toggle-primary mr-2" bind:checked={nostrPreferenceCheckboxChecked} on:change={e => {onChangeNostrPreferenceCheckbox(e)}} disabled />
                        <span class="label-text">Use browser extension's identity</span>
                    </label>
                </div>
                {#if nostrPreferenceCheckboxChecked}
                    <small>You'll sign messages with your extension when you write in the channel.</small>
                {:else}
                    <small>You'll be using your Plebeian Market generated Nostr identity. Install a Nostr browser extension
                        (<a class="link" href="https://github.com/fiatjaf/nos2x" target="_blank" rel="noreferrer">nos2x</a>,
                        <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a> or
                        <a class="link" href="https://www.blockcore.net/wallet" target="_blank" rel="noreferrer">Blockcore</a>) if you want to use your own Nostr identity:</small>
                {/if}
            </div>
        </div>

        <div class="flex border-base-300 bg-info-content-200 rounded-b-box rounded-tr-box
                        min-h-[6rem] min-w-[18rem] max-w-4xl flex-wrap items-center justify-center
                        gap-2 overflow-x-hidden border bg-cover bg-top p-4"
             style="background-size: 5px 5px; background-image: radial-gradient(hsla(var(--bc)/.2) 0.5px,hsla(var(--b2)/1) 0.5px);"
        >
            <div class="w-full h-96 overflow-y-scroll" bind:this={chatArea}>
                {#each sortedMessages as message}
                    <NostrNote {message} {pool}></NostrNote>
                {/each}
            </div>
        </div>
    </div>

    {#if emptyChatShowsLoading && sortedMessages.length === 0}
        <Loading />
    {:else}
        <div class="p-3 bg-black shadow rounded-lg grid grid-cols-9 md:grid-cols-8 grid-rows-1 grid-flow-col gap-4">
            <textarea
                    rows="2"
                    id="nostrMessageSendText"
                    autofocus
                    placeholder="Type the message you want to send to the channel..."
                    bind:this={textarea}
                    on:keypress={onKeyPress}
                    class="col-span-7 w-full p-2 text-white bg-medium placeholder:text-light outline-0 resize-none"></textarea>

            <div on:click={sendMessage}
                 class="col-span-2 md:col-span-1 flex flex-col py-2 p-4 justify-center border-l border-solid border-dark
                 hover:bg-neutral-focus transition-all cursor-pointer text-white">
                <svg xmlns="http://www.w3.org/2000/svg" width="54" height="54" fill="currentColor" class="bi bi-telegram" viewBox="0 0 16 16">
                    <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.05-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09z"/>
                </svg>
            </div>
        </div>
    {/if}
</div>
