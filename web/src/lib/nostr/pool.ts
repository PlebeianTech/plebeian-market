import type {Event, Relay} from "nostr-tools";
import {getEventHash, relayInit, signEvent, validateEvent} from "nostr-tools";
import {timeoutBetweenRelayConnectsMillis, nostrPrivateKey, hasExtension, relayUrlList} from "$lib/nostr/utils";

export class Pool {
    relays: Relay[] = [];

    public async connect(successConnectionCallback = null) {
        for (const relayUrl of relayUrlList) {
            const relay: Relay = relayInit(relayUrl)

            try {
                await relay.connect()
            } catch (e) {
                console.log("   ** Nostr: CATCH: Couldn't connect to ", relayUrl)
            }

            relay.on('connect', () => {
                this.relays.push(relay);

                if (successConnectionCallback !== null) {
                    console.debug('   ** Nostr:   -- Connected to relay: ' + relay.url + ' -- Calling callback:')
                    successConnectionCallback();
                } else {
                    console.debug('   ** Nostr:   -- Connected to relay: ' + relay.url)
                }
            })
            relay.on('error', () => {
                console.log(`   ** Nostr: Failed to connect to relay: ${relay.url}`)
            })

            await new Promise(resolve => setTimeout(resolve, timeoutBetweenRelayConnectsMillis));
        }
    }

    public disconnect() {
        this.relays.forEach(async relay => {
            console.info('   ** Nostr: Closing connection to relay: ' + relay.url)
            await relay.close()
        })
    }

    public async sendMessage(nostrRoomId, message) {
        let nostrPublicKey;

        try {
            nostrPublicKey = await window.nostr.getPublicKey()
        } catch (error) {
            console.error('   ** Nostr: Error getting public key from extension:', error);
            return false;
        }

        let event: Event = {
            kind: 42,
            content: message,
            created_at: Math.floor(Date.now() / 1000),
            tags: [
                ['e', nostrRoomId, "root"]
            ],
            pubkey: nostrPublicKey
        }

        console.debug('   ** Nostr: event before hashing: ', event)
        event.id = getEventHash(event)

        if (!hasExtension || (hasExtension && localStorage.getItem(localStorageNostrPreferPMId) !== null)) {
            // TODO: use PM nostr identify if no extension present
            // ??? event.sig = signEvent(event, nostrPrivateKey)
            // ??? event = signEvent(event, nostrPrivateKey)
        } else {
            try {
                event = await window.nostr.signEvent(event)
            } catch (error) {
                console.error('   ** Nostr: Error signing event in extension:', error);
                return false;
            }

            console.debug('   ** Nostr: event after hashing and signing', event);
        }

        if (validateEvent(event)) {
            this.relays.forEach(relay => {
                console.debug('   ** Nostr: Publishing at relay', relay.url)
                let pub = relay.publish(event)

                pub.on('ok', () => {
                    console.log(`   ** Nostr: ${relay.url} has accepted our event`)
                })
                pub.on('seen', () => {
                    console.log(`   ** Nostr: we saw the event on ${relay.url}`)
                })
                pub.on('failed', reason => {
                    console.log(`   ** Nostr: failed to publish to ${relay.url}: ${reason}`)
                })
            })

            return true;
        } else {
            console.error("   ** Nostr: Event not valid: ", event)
        }

        return false;
    }


    public subscribeToChannel(nostrRoomId, messageLimit, since, callbackFunction) {
        this.relays.forEach(async relay => {
            console.debug('   ** Nostr: Subscribing to channel in relay: ' + relay.url)

            let sub = relay.sub([{
                kinds: [42],
                '#e': [nostrRoomId],
                limit: messageLimit,
                since: since
            }]);

            sub.on('event', event => {
                console.debug('   ** Nostr: Subscribed to channel in relay: ' + relay.url)
                callbackFunction(event)
            });
        })
    }
}
