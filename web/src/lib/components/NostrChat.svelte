<script lang="ts">
    import NostrNote from "$lib/components/NostrNote.svelte";
    import {onDestroy, onMount, beforeUpdate, afterUpdate} from "svelte";
    import {token, user} from "$lib/stores";
    import Loading from "$lib/components/Loading.svelte";
    import {Event, Sub, Filter, generatePrivateKey} from "nostr-tools";
    import {Pool} from "$lib/nostr/pool";
    import {hasExtension, queryNip05, wait, localStorageNostrPreferPMId, nostrEventKinds} from '$lib/nostr/utils';
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

                    if (profileInfo) {
                        if (profileInfo.picture) {
                            message.profileImage = profileInfo.picture
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
                kinds: [nostrEventKinds.metadata],
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
                    nostrEventKinds.note,
                    nostrEventKinds.replies,
                    nostrEventKinds.reactions,
                ],
                '#e': noteInfoToGetLocal
            };

            const sub: Sub = relay.sub([filter]);

            sub.on('event', event => {
                const kind = event.kind;

                // TODO: REPLIES AND LIKES

                if (kind === 7) {
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
            console.error('NostrChat.svelte:onMount - We must have the nostrRoomId at this point');
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
            if (await pool.sendMessage(null, content, $user, nostrRoomId)) {
                textarea.value = '';
            }
        }

        scrollToBottom(chatArea)
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
        <div class="p-3 bg-black hover:shadow-xl duration-300 rounded-lg flex items-center">
            <textarea
                    rows="2"
                    autofocus
                    placeholder="Type the message you want to send to the channel..."
                    bind:this={textarea}
                    on:keypress={onKeyPress}
                    class="w-full p-2 text-white placeholder:text-light outline-0 resize-none"></textarea>

            <div on:click={sendMessage}
                 class="flex flex-col py-2 p-4 justify-center
                 hover:scale-110 duration-300 transition-all cursor-pointer text-white">
                 <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                </svg>
            </div>
        </div>
    {/if}
</div>
