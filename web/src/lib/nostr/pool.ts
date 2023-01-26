import type {Event, Relay} from "nostr-tools";
import {getEventHash, relayInit, signEvent, validateEvent, getPublicKey} from "nostr-tools";
import {timeoutBetweenRelayConnectsMillis, hasExtension, relayUrlList, nostrEventSubscribeToCreateChannel, localStorageNostrPreferPMId} from "$lib/nostr/utils";

export class Pool {
    relays: Relay[] = [];

    public async connectAndSubscribeToChannel(channelInfo = null) {
        for (const relayUrl of relayUrlList) {
            const relay: Relay = relayInit(relayUrl);

            try {
                await relay.connect();
            } catch (e) {
                console.log("   ** Nostr: CATCH: Couldn't connect to ", relayUrl);
                continue;
            }

            relay.on('connect', () => {
                this.relays.push(relay);

                if (channelInfo !== null) {
                    console.debug('   ** Nostr:   -- Connected to relay: ' + relay.url + ' -- Channel info:', channelInfo);

                    this.subscribeToChannel(
                        relay,
                        channelInfo['nostrRoomId'],
                        channelInfo['messageLimit'],
                        channelInfo['since'],
                        channelInfo['callbackFunction']
                    );
                } else {
                    console.debug('   ** Nostr:   -- Connected to relay: ' + relay.url);
                }
            })
            relay.on('error', () => {
                console.log(`   ** Nostr: Failed to connect to relay: ${relay.url}`);
            })

            await new Promise(resolve => setTimeout(resolve, timeoutBetweenRelayConnectsMillis));
        }
    }

    public disconnect() {
        this.relays.forEach(async relay => {
            console.info('   ** Nostr: Closing connection to relay: ' + relay.url);
            await relay.close();
        })
    }

    public async sendMessage(nostrRoomId, message, user) {
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
                return false;
            }
        }

        let event: Event = {
            kind: nostrEventSubscribeToCreateChannel,
            content: message,
            created_at: Math.floor(Date.now() / 1000),
            tags: [
                ['e', nostrRoomId, "root"]
            ],
            pubkey: nostrPublicKey
        };

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
                return false;
            }

            console.debug('   ** Nostr: event after hashing and signing by extension', event);
        }

        if (validateEvent(event)) {
            this.relays.forEach(relay => {
                console.debug('   ** Nostr: Publishing at relay', relay.url);
                let pub = relay.publish(event);

                pub.on('ok', () => {
                    console.log(`   ** Nostr: ${relay.url} has accepted our event`);
                })
                pub.on('seen', () => {
                    console.log(`   ** Nostr: we saw the event on ${relay.url}`);
                })
                pub.on('failed', reason => {
                    console.log(`   ** Nostr: failed to publish to ${relay.url}: ${reason}`);
                })
            })

            return true;
        } else {
            console.error("   ** Nostr: Event not valid: ", event);
        }

        return false;
    }

    public subscribeToChannelEntirePool(nostrRoomId, messageLimit, since, callbackFunction) {
        this.relays.forEach(async relay => {
            console.debug('   ** Nostr: Subscribing to channel in relay: ' + relay.url);

            let sub = relay.sub([{
                kinds: [42],
                '#e': [nostrRoomId],
                limit: messageLimit,
                since: since
            }]);

            sub.on('event', event => {
                console.debug('   ** Nostr: Event received from channel in relay: ' + relay.url);
                callbackFunction(event);
            });
        })
    }

    public subscribeToChannel(relay, nostrRoomId, messageLimit, since, callbackFunction) {
        console.debug('   ** Nostr: Subscribing to channel in relay: ' + relay.url);

        let sub = relay.sub([{
            kinds: [42],
            '#e': [nostrRoomId],
            limit: messageLimit,
            since: since
        }]);

        sub.on('event', event => {
            console.debug('   ** Nostr: Event received from channel in relay: ' + relay.url);
            callbackFunction(event);
        });
    }
}
