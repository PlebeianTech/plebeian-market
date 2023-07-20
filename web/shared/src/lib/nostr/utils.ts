import {getEventHash, nip05, nip19, Kind, getSignature} from "nostr-tools";
import {goto} from "$app/navigation";
import {NostrPrivateKey, NostrPublicKey, NostrLoginMethod} from "$sharedLib/stores.js";
import {get} from "svelte/store";

export const pmChannelNostrRoomId = import.meta.env.VITE_NOSTR_MARKET_SQUARE_CHANNEL_ID;

export const relayUrlList = [
    // Amethyst relays
    "wss://relay.damus.io",
    "wss://relay.nostr.bg",
    "wss://nostr.mom",
    "wss://nos.lol",
    "wss://nostr.bitcoiner.social",
    "wss://nostr-pub.wellorder.net",
    "wss://nostr.wine",
    "wss://eden.nostr.land",
    "wss://relay.orangepill.dev",
    "wss://no.str.cr",
    "wss://puravida.nostr.land",
    "wss://relay.nostr.com.au",
    "wss://nostr.inosta.cc",
    //"wss://relay.taxi"
];

export const pmMasterPublicKey = 'df476caf4888bf5d99c6a710ea6ae943d3e693d29cdc75c4eff1cfb634839bb8';

export function hasExtension() {
    return !!(window as any).nostr;
}

export async function createEvent(kind: number, content: any, tags: any = []) {
    let event: any = {
        kind,
        content,
        tags,
        created_at: Math.floor(Date.now() / 1000),
    }

    if (get(NostrLoginMethod) === 'extension' && hasExtension()) {
        event.pubkey = await (window as any).nostr.getPublicKey();
        event.id = getEventHash(event);
        return await (window as any).nostr.signEvent(event);
    } else {
        let pubKey = get(NostrPublicKey);
        let privKey = get(NostrPrivateKey);

        if (!pubKey || !privKey) {
            return false;
        }

        event.pubkey = pubKey;
        event.id = getEventHash(event);
        event.sig = getSignature(event, privKey);
        return event;
    }
}

export async function wait(milliseconds) {
    await new Promise(resolve => setTimeout(resolve, milliseconds));
}

export function formatTimestamp(ts, show_date_always = false) {
    const today = new Date().setHours(0, 0, 0, 0);
    const thatDay = new Date(ts * 1000).setHours(0, 0, 0, 0);

    let format;

    if (today === thatDay && !show_date_always) {
        format = {
            timeStyle: 'short',
        };
    } else {
       format = {
            dateStyle: 'medium',
            timeStyle: 'short',
        };
    }

    const formatter = new Intl.DateTimeFormat('en-US', format);

    return formatter.format(new Date(ts * 1000));
}

export function getChannelIdForStall(stallPubkey) {
    // Please, don't change any of this, since we're faking channel
    // creation, so we need the same channel ID every time
    const event = {
        kind: Kind.ChannelCreation,
        pubkey: pmMasterPublicKey,
        created_at: 1672837282,
        content: '{"name": "Plebeian Market Stall ' + stallPubkey + '", "about": "Market Stall Square"}',
        tags: [],
    }

    return getEventHash(event);
}

export async function queryNip05(fullname) {
    let profile;

    try {
        profile = await nip05.queryProfile(fullname);
    } catch (e) {
        console.debug("   ** Nostr: Problem while trying to verify nip05 (" + fullname + "):", e);
        return false;
    }

    if (profile && profile.pubkey) {
        return profile.pubkey;
    }

    return false;
}

export function filterTags(tagsArray, tagToFilter) {
    return tagsArray.filter(t => {
        return t[0] === tagToFilter;
    });
}

export function findMarkerInTags(tags, tagType, marker) {
    let found = false;

    tags.forEach(tag => {
        if (tag[0] === tagType && tag[3] === marker) {
            found = true;
        }
    })

    return found;
}

export function getFirstTagValue(tags, tagType) {
    let tagValue = null;

    tags.forEach(tag => {
        if (tagValue === null && tag[0] === tagType) {
            tagValue = tag[1];
        }
    })

    return tagValue;
}

export function getEventReplyingTo(event) {
    if (event.kind !== 1) {
        return undefined;
    }
    const replyTags = event.tags.filter((tag) => tag[0] === 'e');
    if (replyTags.length === 1) {
        return replyTags[0][1];
    }
    const replyTag = event.tags.find((tag) => tag[0] === 'e' && tag[3] === 'reply');
    if (replyTag) {
        return replyTag[1];
    }
    if (replyTags.length > 1) {
        return replyTags[1][1];
    }
    return undefined;
}

export function getBestRelay() {
    // let relays = getPerson(pubkey)?.relays

    return relayUrlList[0];
}

export function decodeNpub(npub: string) {
    let decoded = nip19.decode(npub);
    if (decoded.type !== "npub" || typeof decoded.data !== 'string') {
        throw new Error("NPUB expected.");
    }
    return <string>decoded.data;
}

export function encodeNpub(key: string) {
    return nip19.npubEncode(key);
}

export function newNostrConversation(pubkey) {
    goto('/messages?newMessagePubKey=' + pubkey);
}

export async function tryLoginToBackend(successCB: () => void = () => {}) {
    const apiHost = import.meta.env.VITE_API_BASE_URL;
    const apiUrl = '/api/login/nostr';

    const event = await createEvent(
        1,
        'pleb auth'
    );

    const options = {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(
            event
        )
    };

    try {
        const response = await fetch(apiHost + apiUrl, options);

        if (!response.ok) {
            console.debug("tryLoginToBackend (1) - Could not contact with a backend, so auto-login-to-backend is not done.");
            return false;
        }

        const responseJson = await response.json();

        if (responseJson.success === true && responseJson.token) {
            localStorage.setItem('token', responseJson.token);
            successCB();
        } else {
            console.debug('responseJson.token', responseJson.token);
        }
    } catch (error) {
        console.debug("tryLoginToBackend (2) - Could not contact with a backend, so auto-login-to-backend is not done.");
        return false;
    }
}
