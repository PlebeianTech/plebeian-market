import {getEventHash, nip05} from "nostr-tools";

export const relayUrlList = [
    "nostr.mwmdev.com",
    "wss://nostr-relay.alekberg.net",
    "wss://nostr-pub.wellorder.net",
    "wss://relay.current.fyi",
    "wss://nostr.bitcoiner.social",
    "wss://relay.damus.io",
    "wss://nostr.kollider.xyz",
    "relay.nostrich.de",
    "wss://relay.nostr.ro",
    "wss://relay.nostr.info",
    "wss://nostr.zebedee.cloud",
    "wss://nostr-pub.semisol.dev",
    "wss://nostr.walletofsatoshi.com"
];

export const pmMasterPublicKey = '03b5036dc3db82604307c1964d2b926417a91c3b11ef75ba6ca55019e9b7a62a';
export const pmChannelNostrRoomId = '4211fc228be5af10923f56e60b1b11b8e63bf0ac7dbd3e1e3d767392fdaed4a4'; // Directo 2140
// '25e5c82273a271cb1a840d0060391a0bf4965cafeb029d5ab55350b418953fbb';   // 'Nostr' channel
export const localStorageNostrPreferPMId = 'nostr-prefer-pm-identity';
export const nostrEventKinds = {
    'metadata': 0,
    'note': 1,
    'delete': 5,
    'replies': 6,
    'reactions': 7,
    'createChannel': 40,
    'channelNote': 42
}

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
        kind: nostrEventKinds.createChannel,
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
