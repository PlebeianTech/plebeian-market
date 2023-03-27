import type {Event, Sub, Pub} from "nostr-tools";
import {getEventHash, signEvent, validateEvent, getPublicKey, Kind, SimplePool} from "nostr-tools";
import {hasExtension, relayUrlList, localStorageNostrPreferPMId, filterTags, findMarkerInTags, getBestRelay} from "$lib/nostr/utils";
import {Error} from "../stores";
import type {User} from "$lib/types/user";

export const pmChannelNostrRoomId = import.meta.env.VITE_NOSTR_MARKET_SQUARE_CHANNEL_ID;

export class Pool {
    subscriptions: Sub[] = [];
    user: User | null = null;
    publicKey: string = '';
    writeEnabled: boolean = false;

    public async sendMessage(pool, message: string, nostrRoomId, eventBeingRepliedTo: Event | null) {
        let event: Event = this.getEventToSendNote(message, nostrRoomId, eventBeingRepliedTo);
        return await this.signValidatePublishEvent(pool, event);
    }

    public async sendReaction(pool, message, reaction: string) {
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

        return await this.signValidatePublishEvent(pool, <Event>{
            kind: Kind.Reaction,
            content: reaction,
            tags: [
                ['e', noteId],
                ['p', notePubkey],
            ],
        });
    }

    public async signValidatePublishEvent(pool: SimplePool, event: Event) {
        let signedEvent: Event | false = await this.signValidateEvent(event);

        if (signedEvent !== false) {
            console.log('BBBBB - signedEvent', signedEvent);

            let pub = pool.publish(relayUrlList, event);

            pub.on('ok', () => {console.log('CCCCCCCCCC')});
            pub.on('failed', reason => {
                console.error(`failed to publish: ${reason}`)
            });

            return true;
        }

        return false;
    }

    public async signValidateEvent(event: Event) {
        if (await this.setPoolPublicKey() === false) {
            return false;
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

    public async setPoolPublicKey() {
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

        return true;
    }

    public async deleteNote(pool: SimplePool, message) {
        const noteId = message.id;

        // TODO: Dialog confirm delete

        return await this.signValidatePublishEvent(pool, <Event>{
            kind: Kind.EventDeletion,
            content: 'deleted',
            created_at: 0,
            tags: [
                ['e', noteId]
            ],
            pubkey: "",
        });
    }

    public unsubscribeEverything() {
        this.subscriptions.forEach(async subscription => {
            console.debug('   ** Nostr: Unsubscribing');
            await subscription.unsub();
        })
    }
}
