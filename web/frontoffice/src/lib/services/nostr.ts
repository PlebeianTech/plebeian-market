import {
    getEventHash,
    Kind,
    type Event,
    type Sub,
    type Filter,
    nip04,
    signEvent
} from 'nostr-tools';
import { UserResume } from "$lib/types/user";
import { relayUrlList, getBestRelay, filterTags, findMarkerInTags } from "$lib/nostr/utils";
import {hasExtension} from "../nostr/utils";
import {NostrPool, NostrPrivateKey, NostrPublicKey} from "../stores";
import {get} from "svelte/store";

export type UserMetadata = {
    name?: string;
    about?: string;
    picture?: string;
    nip05?: string;
};

const EVENT_KIND_PM = 4;
const EVENT_KIND_RESUME = 66;
const EVENT_KIND_STALL = 30017;
const EVENT_KIND_PRODUCT = 30018;
const EVENT_KIND_APP_SETUP = 30078;     // https://github.com/nostr-protocol/nips/blob/master/78.md

const SITE_SPECIFIC_CONFIG_KEY = 'plebeian_market/site_specific_config/v1';

async function createEvent(kind: number, content: any, tags: any = []) {
    let event: any = {
        kind,
        content,
        tags,
        created_at: Math.floor(Date.now() / 1000),
    }

    if (hasExtension()) {
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
console.log('EVENT', event);
        event.id = getEventHash(event);
        event.sig = signEvent(event, privKey);
        return event;
    }
}

export async function closePool() {
    await get(NostrPool).close(relayUrlList);
}

export function subscribeResumes(receivedCB: (pubkey: string, resume: UserResume, createdAt: number) => void) {
    let sub = get(NostrPool).sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME] }]);
    sub.on('event', e => receivedCB(e.pubkey, UserResume.fromJson(JSON.parse(e.content)), e.created_at));
}

export function subscribeResume(pubkey: string, receivedCB: (resume: UserResume, createdAt: number) => void) {
    let sub = get(NostrPool).sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME], authors: [pubkey] }]);
    sub.on('event', e => receivedCB(UserResume.fromJson(JSON.parse(e.content)), e.created_at));
}

export async function publishResume(resume: UserResume, successCB: () => void) {
    const event = await createEvent(EVENT_KIND_RESUME, JSON.stringify(resume.toJson()));
    get(NostrPool).publish(relayUrlList, event).on('ok', successCB);
}

export function subscribeMetadata(pubkeys: string[], receivedCB: (pubkey: string, metadata: UserMetadata) => void) {
    let sub = get(NostrPool).sub(relayUrlList, [{ kinds: [Kind.Metadata], authors: pubkeys }]);
    sub.on('event', e => receivedCB(e.pubkey, JSON.parse(e.content)));
}

export function subscribeReactions(listOfNotesToGetInfo, receivedCB: (event) => void) {
    get(NostrPool).sub(relayUrlList, [{ kinds: [ Kind.Text, Kind.Reaction ], '#e': listOfNotesToGetInfo }]).on('event', receivedCB);
}

export function subscribeChannel(nostrRoomId, messageLimit, since, receivedCB : (event) => void) {
    get(NostrPool).sub(relayUrlList, [{ kinds: [Kind.ChannelMessage], '#e': [nostrRoomId], limit: messageLimit, since: since }]).on('event', receivedCB);
}

function getReplyTags(eventBeingRepliedTo: Event) {
    let tagsToBeAddedToEvent: Array<Array<string>> = [];

    let url = getBestRelay();

    // - adding all "p" from the event being replied to
    for (const pTag of filterTags(eventBeingRepliedTo.tags, 'p')) {
        tagsToBeAddedToEvent.push(pTag);
    }
    // - adding a "p" tag with the pubkey of the creator of the event being replied to
    tagsToBeAddedToEvent.push(['p', eventBeingRepliedTo.pubkey, url]);

    // - "e" tag
    const eTags = filterTags(eventBeingRepliedTo.tags, 'e');
    if (eTags.length === 0 || !findMarkerInTags(eTags, 'e', 'reply')) {
        tagsToBeAddedToEvent.push(['e', eventBeingRepliedTo.id, url, 'root']);
    } else {
        tagsToBeAddedToEvent.push(['e', eventBeingRepliedTo.id, url, 'reply']);
    }

    return tagsToBeAddedToEvent;
}

export async function sendMessage(message: string, roomId: string | null, eventBeingRepliedTo: Event | null, successCB: () => void) {
    let kind, tags;
    if (roomId === null) {
        kind = Kind.Text;
        tags = [];
    } else {
        kind = Kind.ChannelMessage;
        tags = [['e', roomId, getBestRelay(), "root"]];
    }

    if (eventBeingRepliedTo !== null && [Kind.Text, Kind.ChannelMessage].includes(eventBeingRepliedTo.kind)) {
        tags = tags.concat(getReplyTags(eventBeingRepliedTo));
    }

    const event = await createEvent(kind, message, tags);

    get(NostrPool).publish(relayUrlList, event).on('ok', successCB);
}

export async function sendReaction(noteId: string, notePubkey: string, reaction: string, successCB: () => void = () => {}) {
    if (reaction.length !== 1) {
        console.error("Nostr: trying to send reactions with > 1 character is not allowed by NIP-25!");
        return;
    }

    const event = await createEvent(Kind.Reaction, reaction, [['e', noteId], ['p', notePubkey]]);

    get(NostrPool).publish(relayUrlList, event).on('ok', successCB);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// nip-15
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

export function getStalls(merchantPubkey: string | string[] | null, receivedCB: (e) => void) {
    let filter: Filter = { kinds: [EVENT_KIND_STALL] };

    if (merchantPubkey) {
        if (Array.isArray(merchantPubkey)) {
            filter.authors = merchantPubkey;
        } else {
            filter.authors = [merchantPubkey];
        }
    }

    let sub: Sub = get(NostrPool).sub(relayUrlList, [filter]);
    sub.on('event',  e => receivedCB(e));
    sub.on('eose', () => {
        // sub.unsub()
    })
}

export function getProducts(merchantPubkey: string | null, receivedCB: (e) => void) {
    let filter: Filter = { kinds: [EVENT_KIND_PRODUCT] };

    if (merchantPubkey) {
        filter.authors = [merchantPubkey];
    }

    let sub: Sub = get(NostrPool).sub(relayUrlList, [filter]);
    sub.on('event',  e => {receivedCB(e);});
    sub.on('eose', () => {
        // sub.unsub()
    })
}

export async function sendPrivateMessage(receiverPubkey: string, message: string, successCB) {
    let cipheredMessage;
    if (hasExtension()) {
        cipheredMessage = await (window as any).nostr.nip04.encrypt(receiverPubkey, message);
    } else {
        cipheredMessage = await nip04.encrypt(get(NostrPrivateKey), receiverPubkey, message);
    }

    const event = await createEvent(EVENT_KIND_PM, cipheredMessage, [['p', receiverPubkey]]);
    get(NostrPool).publish(relayUrlList, event).on('ok', successCB);
}

export async function getPrivateMessages(userPubkey: string, receivedCB, eoseCB) {
    let sub = get(NostrPool).sub(relayUrlList, [
        {
            kinds: [EVENT_KIND_PM],
            authors: [userPubkey]       // My messages (output)
        },
        {
            kinds: [EVENT_KIND_PM],
            '#p': [userPubkey],         // Replies (input)
        },
    ]);
    sub.on('event', async (e) => {
        const content = e.content;
        const messagePubkey = e.pubkey;

        let decryptPubkey;
        let sender: string | null = null;
        if (messagePubkey === userPubkey) {
            sender = e.tags.find(([k, v]) => k === 'p' && v && v !== '')[1];
            decryptPubkey = sender;         // My messages (output)
        } else {
            decryptPubkey = messagePubkey;  // Replies
        }

        let decryptedContent;
        if (hasExtension()) {
            decryptedContent = await (window as any).nostr.nip04.decrypt(decryptPubkey, content);
        } else {
            let privateKey = get(NostrPrivateKey);
            if (privateKey) {
                decryptedContent = nip04.decrypt(privateKey, decryptPubkey, content);
            } else {
                return false;
            }
        }

        try {
            let jsonDecodedMessage = JSON.parse(decryptedContent);
            jsonDecodedMessage.created_at = e.created_at;
            jsonDecodedMessage.pubkey = messagePubkey;
            jsonDecodedMessage.contentType = 'json';
            receivedCB(jsonDecodedMessage);
        } catch (error) {
            let humanMessage = {
                id: e.id,
                message: decryptedContent,
                created_at: e.created_at,
                pubkey: e.pubkey,
                contentType: 'human',
            };

            if (sender) {
                humanMessage.sender = sender;
            }

            receivedCB(humanMessage);
        }
    });
    sub.on('eose', async () => {
        if (eoseCB) {
            eoseCB();
        }
    });
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// NIP-78
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

export async function publishConfiguration(setup: object, tags, successCB: () => void) {
    const event = await createEvent(
        EVENT_KIND_APP_SETUP,
        JSON.stringify(setup),
        [
            ['p', SITE_SPECIFIC_CONFIG_KEY],
        ]
    );
    get(NostrPool).publish(relayUrlList, event).on('ok', successCB);
}

export function subscribeConfiguration(pubkey: string, receivedCB: (setup: string, createdAt: number) => void) {
    let sub = get(NostrPool).sub(
        relayUrlList,
        [
            {
                kinds: [EVENT_KIND_APP_SETUP],
                authors: [pubkey],
                '#p': [SITE_SPECIFIC_CONFIG_KEY],
            }
        ]
    );
    sub.on('event', e => receivedCB(JSON.parse(e.content), e.created_at));
}
