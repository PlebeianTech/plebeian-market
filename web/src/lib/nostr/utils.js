import {getEventHash, generatePrivateKey, getPublicKey, nip19} from "nostr-tools";
import { ErrorHandler, putProfile } from "$lib/services/api";
export const relayUrlList = [
    "wss://relay.nostr.ro",
    "wss://nostr-relay.alekberg.net",
    "wss://btc.klendazu.com",
    "wss://relay.nostr.info",
    "wss://nostr.onsats.org",
    "wss://nostr-relay.wlvs.space",
    "wss://nostr.bitcoiner.social",
    "wss://relay.damus.io",
    "wss://nostr.zebedee.cloud",
    "wss://relay.nostr.info",
    "wss://nostr-pub.semisol.dev",
    "wss://nostr.walletofsatoshi.com",
];

export const pmMasterPublicKey = '03b5036dc3db82604307c1964d2b926417a91c3b11ef75ba6ca55019e9b7a62a';
export const pmChannelNostrRoomId = '25e5c82273a271cb1a840d0060391a0bf4965cafeb029d5ab55350b418953fbb';   // 'Nostr' channel
export const localStorageNostrPreferPMId = 'nostr-prefer-pm-identity';
export const nostrEventKindCreateChannel = 40;
export const nostrEventSubscribeToCreateChannel = 42;
export const timeoutBetweenRelayConnectsMillis = 50;
export let nostrPublicKeyFromExtension = false;

export function hasExtension() {
    return !!window.nostr;
}

export async function wait(milliseconds) {
    await new Promise(resolve => setTimeout(resolve, milliseconds));
}

export const formatTimestamp = ts => {
    const formatter = new Intl.DateTimeFormat('en-US', {
        dateStyle: 'medium',
        timeStyle: 'short',
    });

    return formatter.format(new Date(ts * 1000));
}

export function getChannelIdFromChannelName(channelName) {
    console.debug('   ** Nostr: Stall channel name: ', channelName);

    // Don't change this, since we're faking channel
    // creation, so we need the same channel ID every time
    let created_at = 1672837282;

    let event = {
        kind: nostrEventKindCreateChannel,
        pubkey: pmMasterPublicKey,
        created_at: created_at,
        content: '{"name": "' + channelName + '", "about": "Plebeian Market Stall Square."}',
        tags: [],
    }

    return getEventHash(event);
}

function createNostrKeys() {
    // hex strings
    let privateKey = generatePrivateKey()
    let publicKey = getPublicKey(privateKey);

    return {
        'private': privateKey,
        'public': publicKey,
        'npub': nip19.npubEncode(publicKey)
    };
}

export function getNostrKeysInitIfNecessary(user, token) {
    if (user.nostr_private_key !== null) {
        let publicKey = getPublicKey(user.nostr_private_key)
        return {
            'private': user.nostr_private_key,
            'public': publicKey,
            'npub': nip19.npubEncode(publicKey)
        };
    }

    let nostrKeys = createNostrKeys();
    let nostr_private_key = nostrKeys.private;

    putProfile(token, {nostr_private_key},
        u => {
            user.set(u);
            console.debug('   ** Nostr: keys saved into user', u)
        },
        new ErrorHandler(true)
    );

    return nostrKeys;
}
