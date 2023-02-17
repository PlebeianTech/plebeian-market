import type {Event, Relay, Sub, Pub} from "nostr-tools";
import {getEventHash, relayInit, signEvent, validateEvent, getPublicKey, Kind} from "nostr-tools";
import {hasExtension, relayUrlList, localStorageNostrPreferPMId, filterTags, findMarkerInTags, getBestRelay} from "$lib/nostr/utils";
import {Error} from "../stores";
import type {User} from "$lib/types/user";

export const pmChannelNostrRoomId = import.meta.env.VITE_NOSTR_MARKET_SQUARE_CHANNEL_ID;

export class Pool {
    relays: Map<string, Relay> = new Map<string, Relay>();
    subscriptions: Sub[] = [];
    user: User | null = null;
    publicKey: string = '';
    writeEnabled: boolean = false;

    public async connectAndSubscribeToChannel(channelInfo = null) {
        let that = this;

        for (const relayUrl of relayUrlList) {
            this.getRelayOrConnect(relayUrl)
                .then(async function (relay) {
                    if (channelInfo !== null) {
                        console.debug('   ** Nostr:   -- Connected to relay: ' + relay.url + ' -- Channel info:', channelInfo);

                        that.subscribeToChannel(
                            relay,
                            channelInfo['nostrRoomId'],
                            channelInfo['messageLimit'],
                            channelInfo['since'],
                            channelInfo['callbackFunction']
                        );
                    }

                }, function(error) {
                    console.error("*** - connectAndSubscribeToChannel - ", error);
                });
        }
    }

    /*
    Will connect to each Nostr relay in relayUrlList and send them
    the message. It will reuse the connection if already connected.
     */
    public async connectAndSendMessage(messageInfo = null) {
        if (messageInfo === null) {
            return false;
        }

        // 1
        let event: Event = this.getEventToSendNote(messageInfo['message'], messageInfo['nostrRoomId'], null);

        // 2
        let signedEvent = await this.signValidateEvent(event);

        let that = this;

        // 3
        if (signedEvent !== false) {
            for (const relayUrl of relayUrlList) {
                this.getRelayOrConnect(relayUrl)
                    .then(async function (relay) {
                        await that.publishEvent(<Relay> relay, <Event> signedEvent);
                    }, function(error) {
                        console.error(`   ** Nostr: Failed to connect to relay:`, error);
                    });
            }
        }
    }

    private getRelayOrConnect(relayUrl: string) {
        let that = this;

        return new Promise(async function (resolve, reject) {
            let relay: Relay | undefined = that.relays.get(relayUrl);

            if (relay !== undefined) {
                resolve(relay);
            } else {
                try {
                    let newRelay = relayInit(relayUrl);

                    newRelay.on('connect', () => {
                        console.debug('   ** Nostr:   -- Connected to relay: ' + relayUrl);
                        that.relays.set(relayUrl, newRelay);
                        resolve(newRelay);
                    })
                    newRelay.on('error', () => {
                        console.log(`   ** Nostr: Failed to connect to relay: ${newRelay.url}`);
                        reject("Couldn't connect to relay (onError): " + relayUrl);
                    })

                    await newRelay.connect();

                } catch (e) {
                    reject("Couldn't connect to relay (catch): " + relayUrl);
                }
            }
        });
    }

    /*
    The process of publishing Nostr events have 3 parts:

    1- Create an event of type Event. You can put a blank in
    the pubkey field as it's mandatory, but you probably
    don't have it yet. You can do it "manually" by creating
    an object of type Event or use helper functions like
    `getEventToSendNote`.

    2- `signValidateEvent`: puts the public key into the event,
    then sign it with the key found on your Nostr extension
    (or the Plebeian Market one if you don't have an extension)
    and validate that it's correct.

    3- `publishEvent`: it publishes the event to the relay
    specified, or all the connected relays in the pool if
    relay is null.

    If you don't need to do any special treatment to the
    event, you can call `sendMessage` which will do all the
    phases: creating the event (1), signing and validating
    the event (2), and publishing to the relays (3).

    There is also a function to do steps 2 and 3 in one step
    called `signValidatePublishEvent`.
     */

    async sendMessage(relay: Relay, message: string, nostrRoomId, eventBeingRepliedTo: Event | null) {
        let event: Event = this.getEventToSendNote(message, nostrRoomId, eventBeingRepliedTo);
        return await this.signValidatePublishEvent(event);
    }

    public getEventToSendNote(message: string, nostrRoomId, eventBeingRepliedTo: Event | null): Event {
        let event: Event;

        if (nostrRoomId === false) {
            event = {
                kind: Kind.Text,
                content: message,
                created_at: 0,
                tags: [],
                pubkey: ''
            };
        } else {
            event = {
                kind: Kind.ChannelMessage,
                content: message,
                created_at: 0,
                tags: [
                    ['e', nostrRoomId, getBestRelay(), "root"]
                ],
                pubkey: ''
            };
        }

        if (eventBeingRepliedTo !== null && [Kind.Text, Kind.ChannelMessage].includes(eventBeingRepliedTo.kind)) {
            event.tags = event.tags.concat(this.getReplyTagsToEvent(eventBeingRepliedTo));
        }

        return event;
    }

    public getReplyTagsToEvent(eventBeingRepliedTo: Event) {
        let tagsToBeAddedToEvent: Array<Array<string>> = [];

        let url = getBestRelay();

        // ** Tag P
        //      - Adding all P from the event being replied to
        filterTags(eventBeingRepliedTo.tags, 'p').forEach(tagP => {
            tagsToBeAddedToEvent.push(tagP);
        });
        //      - Adding a P tag with the pubkey of the creator of the event being replied to
        tagsToBeAddedToEvent.push(['p', eventBeingRepliedTo.pubkey, url]);

        // ** Tag E
        const eventBeingRepliedToTagsE = filterTags(eventBeingRepliedTo.tags, 'e');
        if (eventBeingRepliedToTagsE.length === 0 || !findMarkerInTags(eventBeingRepliedToTagsE, 'e', 'reply')) {
            tagsToBeAddedToEvent.push(['e', eventBeingRepliedTo.id, url, 'root']);
        } else {
            tagsToBeAddedToEvent.push(['e', eventBeingRepliedTo.id, url, 'reply']);
        }

        return tagsToBeAddedToEvent;
    }

    public async signValidateEvent(event: Event) {
        if (!hasExtension() || (hasExtension() && localStorage.getItem(localStorageNostrPreferPMId) !== null)) {
            // Using PM Nostr identity
            let userPrivateKey = this.user?.nostr_private_key || null;

            if (userPrivateKey === null) {
                return false;
            }

            this.publicKey = getPublicKey(userPrivateKey);

            if (!this.publicKey) {
                console.debug('   ** Nostr: Not using extension, but PM identity (public key) not available.');
                return false;
            }

        } else {
            // Using Nostr extension identity
            try {
                this.publicKey = await window.nostr.getPublicKey();
            } catch (error) {
                console.error('   ** Nostr: Error getting public key from extension:', error);
                Error.set("Error getting the Nostr public key from your extension.");
                return false;
            }
        }

        console.debug('   ** Nostr: event before adding missing properties: ', event);

        event.created_at = Math.floor(Date.now() / 1000);
        event.pubkey = this.publicKey;
        event.id = getEventHash(event);

        if (!hasExtension() || (hasExtension() && localStorage.getItem(localStorageNostrPreferPMId) !== null)) {
            // Using PM Nostr identity
            let userPrivateKey = this.user?.nostr_private_key || null;

            if (userPrivateKey === null) {
                console.debug('   ** Nostr: Not using extension, but PM identity (private key) not available.')
                return false;
            }

            event.sig = signEvent(event, userPrivateKey);
            console.debug('   ** Nostr: event after hashing and signing by PM Nostr keys', event);
        } else {
            // Using Nostr extension identity
            try {
                event = await window.nostr.signEvent(event);
            } catch (error) {
                console.error('   ** Nostr: Error signing event in extension:', error);
                Error.set("Error getting permissions to sign the message from your Nostr extension.");
                return false;
            }

            console.debug('   ** Nostr: event after hashing and signing by extension', event);
        }

        if (validateEvent(event)) {
            return event;
        }

        return false;
    }

    public async publishEvent(relay: Relay | null, event: Event) {
        if (relay !== null) {
            this.publishEventToRelay(relay, event);
        } else {
            // No relay provided, so send to all the relays in the pool
            this.relays.forEach(relay => {
                this.publishEventToRelay(relay, event);
            })
        }

        return true;
    }

    publishEventToRelay(relay: Relay, event: Event) {
        console.debug('   ** Nostr: Publishing at relay', relay.url);
        let pub: Pub = relay.publish(event);

        pub.on('ok', () => {
            console.log(`   ** Nostr: ${relay.url} has accepted our event`);
        })
        pub.on('failed', reason => {
            console.log(`   ** Nostr: failed to publish to ${relay.url}: ${reason}`);
        })
    }

    public async sendReaction(message, reaction: string) {
        if (!this.writeEnabled) {
            Error.set('You need to either use a Nostr extension for your browser or register into Plebeian Market so we can provide one for you');
            return;
        }

        const noteId = message.id;
        const notePubkey = message.pubkey;

        console.debug('   ** Nostr: ******* Sending reaction: ' + reaction + ' to note with Id: ' + noteId + ' pubkey: ' + notePubkey);

        if (reaction.length !== 1) {
            console.error('   ** Nostr: trying to send reactions with > 1 character is not allowed by nip-25');
            return;
        }

        if (!noteId || !notePubkey) {
            return false;
        }

        return await this.signValidatePublishEvent(<Event>{
            kind: Kind.Reaction,
            content: reaction,
            tags: [
                ['e', noteId],
                ['p', notePubkey],
            ],
        });
    }

    public async signValidatePublishEvent(event: Event) {
        let signedEvent: Event | false = await this.signValidateEvent(event);

        if (signedEvent !== false) {
            if (await this.publishEvent(null, <Event> signedEvent)) {
                return true;
            }
        }

        return false;
    }

    public async deleteNote(message) {
        const noteId = message.id;

        // TODO: Dialog confirm delete

        return await this.signValidatePublishEvent({
            kind: Kind.EventDeletion,
            content: 'deleted',
            created_at: 0,
            tags: [
                ['e', noteId]
            ],
            pubkey: "",
        });
    }

    public subscribeToChannel(relay: Relay, nostrRoomId, messageLimit, since, callbackFunction) {
        console.debug('   ** Nostr: Subscribing to channel in relay: ' + relay.url);

        let sub: Sub = relay.sub([{
            kinds: [Kind.ChannelMessage],
            '#e': [nostrRoomId],
            limit: messageLimit,
            since: since
        }]);

        sub.on('event', event => {
            console.debug('   ** Nostr: Event received from channel in relay: ' + relay.url);
            callbackFunction(event);
        });

        this.subscriptions.push(sub);
    }

    public unsubscribeEverything() {
        this.subscriptions.forEach(async subscription => {
            console.debug('   ** Nostr: Unsubscribing');
            await subscription.unsub();
        })
    }

    public disconnect() {
        this.relays.forEach(async relay => {
            console.debug('   ** Nostr: Closing connection to relay: ' + relay.url);
            await relay.close();
        })
    }
}
