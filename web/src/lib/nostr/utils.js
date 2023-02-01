import {getEventHash, nip05} from "nostr-tools";

export const relayUrlList = [
    "wss://relay.nostr.ro",
    "wss://nostr-relay.alekberg.net",
    "wss://btc.klendazu.com",
    "wss://relay.nostr.info",
    "wss://nostr.onsats.org",
    "wss://eden.nostr.land",
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

export function getChannelIdForStallOwner(user) {
    let stallName = 'Plebeian Market Stall ' + user.identity + ' (' + import.meta.env.MODE + ')';

    console.debug('   ** Nostr: Stall channel name: ', stallName);

    // Please, don't change this, since we're faking channel
    // creation, so we need the same channel ID every time
    let created_at = 1672837282;

    let event = {
        kind: nostrEventKindCreateChannel,
        pubkey: pmMasterPublicKey,
        created_at: created_at,
        content: '{"name": "' + stallName + '", "about": "Plebeian Market Stall Square."}',
        tags: [],
    }

    return getEventHash(event);
}

export async function queryNip05(fullname) {
    let profile;

    try {
        profile = await nip05.queryProfile(fullname)
    } catch (e) {
        console.debug("   ** Nostr: Problem while trying to verify nip05 (" + fullname + "):", e);
        return false;
    }

    if (profile && profile.pubkey) {
        return profile.pubkey;
    }

    return false;
}
