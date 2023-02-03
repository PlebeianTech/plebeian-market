import type {Event, Relay, Sub, Pub} from "nostr-tools";
import {getEventHash, relayInit, signEvent, validateEvent, getPublicKey} from "nostr-tools";
import {timeoutBetweenRelayConnectsMillis, hasExtension, relayUrlList, nostrEventKinds, localStorageNostrPreferPMId, wait, pmChannelNostrRoomId} from "$lib/nostr/utils";
import {Error, user} from "../stores";

export class Pool {
    relays: Map<string, Relay> = new Map<string, Relay>();
    subscriptions: Sub[] = [];

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

                    // await wait(timeoutBetweenRelayConnectsMillis);
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

        let event = await this.createEvent(
            messageInfo['message'],
            messageInfo['user'],
            messageInfo['nostrRoomId']
        );

        let that = this;

        if (event !== false) {
            for (const relayUrl of relayUrlList) {
                this.getRelayOrConnect(relayUrl)
                    .then(async function (relay) {
                        await that.sendEvent(<Relay> relay, <Event> event);
                    }, function(error) {
                        console.error(`   ** Nostr: Failed to connect to relay:`, error);
                    });

                //await wait(timeoutBetweenRelayConnectsMillis);
            }
        }
    }

    private getRelayOrConnect(relayUrl: string) {
        let that = this;

        return new Promise(async function (resolve, reject) {
            let relay: Relay | undefined = that.relays.get(relayUrl);

            if (relay !== undefined) {
                console.log('*************** RELAY YA CONECTADO. SE DEVUELVE: ', relayUrl);
                resolve(relay);
            } else {
                console.log('*************** CONECTANDO A RELAY POR PRIMERA VEZ !! ', relayUrl);
                try {
                    let newRelay = relayInit(relayUrl);
                    await newRelay.connect();

                    newRelay.on('connect', () => {
                        console.debug('   ** Nostr:   -- Connected to relay: ' + relayUrl);
                        that.relays.set(relayUrl, newRelay);
                        resolve(newRelay);
                    })
                    newRelay.on('error', () => {
                        console.log(`   ** Nostr: Failed to connect to relay: ${newRelay.url}`);
                        reject("Couldn't connect to relay (onError): " + relayUrl);
                    })
                } catch (e) {
                    reject("Couldn't connect to relay (catch): " + relayUrl);
                }
            }
        });
    }

    /*
    The process of sending Nostr messages have 2 parts:

    1- `createEvent`: it creates the event, put the required
    properties, sign and validate it.

    2- `sendEvent`: it publishes the event to the relay
    specified, or all the relays if relay is null.

    If you don't need to do any special treatment to the
    event, you can call `sendMessage` which will do both
    creating the event (1) and publishing to the relays (2).
     */

    async sendMessage(relay: Relay, message: string, user, nostrRoomId) {
        let event = await this.createEvent(
            message,
            user,
            nostrRoomId
        );

        if (event !== false) {
            if (await this.sendEvent(relay, <Event>event)) {
                return true;
            }
        }

        return false;
    }

    public async createEvent(message: string, user, nostrRoomId) {
        let nostrPublicKey;

        if (!hasExtension() || (hasExtension() && localStorage.getItem(localStorageNostrPreferPMId) !== null)) {
            // PM Nostr identity
            nostrPublicKey = getPublicKey(user.nostr_private_key);

            if (!nostrPublicKey) {
                console.debug('   ** Nostr: Not using extension, but PM identity (public key) not available.');
                return false;
            }

        } else {
            // Nostr extension identity
            try {
                nostrPublicKey = await window.nostr.getPublicKey();
            } catch (error) {
                console.error('   ** Nostr: Error getting public key from extension:', error);
                Error.set("Error getting the Nostr public key from your extension.");
                return false;
            }
        }

        let event: Event;

        if (nostrRoomId === false) {
            event = {
                kind: nostrEventKinds.note,
                content: message,
                created_at: Math.floor(Date.now() / 1000),
                tags: [],
                pubkey: nostrPublicKey
            };
        } else {
            event = {
                kind: nostrEventKinds.channelNote,
                content: message,
                created_at: Math.floor(Date.now() / 1000),
                tags: [
                    ['e', nostrRoomId, "root"]
                ],
                pubkey: nostrPublicKey
            };
        }

        console.debug('   ** Nostr: event before hashing: ', event)
        event.id = getEventHash(event)

        if (!hasExtension() || (hasExtension() && localStorage.getItem(localStorageNostrPreferPMId) !== null)) {
            // PM Nostr identity
            let nostrPrivateKey = user.nostr_private_key;

            if (!nostrPrivateKey) {
                console.debug('   ** Nostr: Not using extension, but PM identity (private key) not available.')
                return false;
            }

            event.sig = signEvent(event, nostrPrivateKey);
            console.debug('   ** Nostr: event after hashing and signing by PM Nostr keys', event);
        } else {
            // Nostr extension identity
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

    public async sendEvent(relay: Relay, event: Event) {
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
        pub.on('seen', () => {
            console.log(`   ** Nostr: we saw the event on ${relay.url}`);
        })
        pub.on('failed', reason => {
            console.log(`   ** Nostr: failed to publish to ${relay.url}: ${reason}`);
        })
    }

    public subscribeToChannel(relay: Relay, nostrRoomId, messageLimit, since, callbackFunction) {
        console.debug('   ** Nostr: Subscribing to channel in relay: ' + relay.url);

        let sub: Sub = relay.sub([{
            kinds: [nostrEventKinds.channelNote],
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
