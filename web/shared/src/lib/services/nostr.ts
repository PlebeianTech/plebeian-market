import {
    Kind,
    type Event,
    type Sub,
    type Filter,
    nip04
} from 'nostr-tools';
import {get} from "svelte/store";
import { UserResume } from "$sharedLib/types/user";
import {hasExtension, relayUrlList, getBestRelay, filterTags, findMarkerInTags, createEvent} from "$sharedLib/nostr/utils";
import {NostrPool, NostrPrivateKey, NostrLoginMethod} from "$sharedLib/stores";
import {loggedIn, waitAndShowLoginIfNotLoggedAlready} from "$sharedLib/utils";

export type UserMetadata = {
    name?: string;
    about?: string;
    picture?: string;
    nip05?: string;
};

const EVENT_KIND_PM = 4;
const EVENT_KIND_RESUME = 66;
const EVENT_KIND_STALL = 30017;
export const EVENT_KIND_PRODUCT = 30018;
export const EVENT_KIND_AUCTION = 30020;
export const EVENT_KIND_AUCTION_BID = 1021;
export const EVENT_KIND_AUCTION_BID_STATUS = 1022;

/* Badges (nip-58) */
const EVENT_KIND_BADGE_AWARD = 8;
const EVENT_KIND_PROFILE_BADGES = 30008;
const EVENT_KIND_BADGE_DEFINITION = 30009;

const EVENT_KIND_APP_SETUP = 30078;     // https://github.com/nostr-protocol/nips/blob/master/78.md

const SITE_SPECIFIC_CONFIG_KEY = 'plebeian_market/site_specific_config/v1';

export async function closePool() {
    await get(NostrPool).close(relayUrlList);
}

export function getNostrEvent(listOfEventIds, receivedCB: (event) => void, eoseCB) {
    const sub = get(NostrPool)
        .sub(relayUrlList, [{ 'ids': listOfEventIds }]);
    sub.on('event', receivedCB);
    if (eoseCB) {
        sub.on('eose', eoseCB);
    }
}

export function subscribeResumes(receivedCB: (pubkey: string, resume: UserResume, createdAt: number) => void) {
    const sub = get(NostrPool).sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME] }]);
    sub.on('event', e => receivedCB(e.pubkey, UserResume.fromJson(JSON.parse(e.content)), e.created_at));
}

export function subscribeResume(pubkey: string, receivedCB: (resume: UserResume, createdAt: number) => void) {
    const sub = get(NostrPool).sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME], authors: [pubkey] }]);
    sub.on('event', e => receivedCB(UserResume.fromJson(JSON.parse(e.content)), e.created_at));
}

export async function publishResume(resume: UserResume, successCB: () => void) {
    const event = await createEvent(EVENT_KIND_RESUME, JSON.stringify(resume.toJson()));
    get(NostrPool)
        .publish(relayUrlList, event)
        .on('ok', successCB);
}

export function subscribeReactions(listOfNotesToGetInfo, receivedCB: (event) => void) {
    get(NostrPool)
        .sub(relayUrlList, [{ kinds: [ Kind.Text, Kind.Reaction ], '#e': listOfNotesToGetInfo }])
        .on('event', receivedCB);
}

export function subscribeChannel(nostrRoomId, messageLimit, since, receivedCB : (event) => void) {
    get(NostrPool)
        .sub(relayUrlList, [{ kinds: [Kind.ChannelMessage], '#e': [nostrRoomId], limit: messageLimit, since: since }])
        .on('event', receivedCB);
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

export async function sendMessage(message: string, roomId: string | null, eventBeingRepliedTo: Event | null, kind: number | null, successCB: () => void) {
    let eventKind, tags;
    if (roomId === null) {
        eventKind = kind ?? Kind.Text;
        tags = [];
    } else {
        eventKind = kind ?? Kind.ChannelMessage;
        tags = [['e', roomId, getBestRelay(), "root"]];
    }

    if (eventBeingRepliedTo !== null && [Kind.Text, Kind.ChannelMessage, EVENT_KIND_AUCTION].includes(eventBeingRepliedTo.kind)) {
        tags = tags.concat(getReplyTags(eventBeingRepliedTo));
    }

    const event = await createEvent(eventKind, message, tags);

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

/**
 * @param {string} recipientPubkey - the public key of the Nostr account where we're sending the message
 * @param {string} message - the message content
 * @param {string} merchantPrivateKey - (optional) if available, the message will be sent using this private key.
 *              This is used to reply to messages as a merchant, and not with the logged-in personal account.
 * @param successCB
 */
export async function sendPrivateMessage(recipientPubkey: string, message: string, merchantPrivateKey: string | boolean, successCB) {
    let cipheredMessage;

    if (loggedIn()) {
        if (!merchantPrivateKey) {
            if (get(NostrLoginMethod) === 'extension' && hasExtension()) {
                cipheredMessage = await (window as any).nostr.nip04.encrypt(recipientPubkey, message);
            } else {
                cipheredMessage = await nip04.encrypt(get(NostrPrivateKey), recipientPubkey, message);
            }
        } else {
            cipheredMessage = await nip04.encrypt(merchantPrivateKey, recipientPubkey, message);
        }
    } else {
        if (!await waitAndShowLoginIfNotLoggedAlready()) {
            return;
        }
        await sendPrivateMessage(recipientPubkey, message, merchantPrivateKey, successCB);
    }

    const event = await createEvent(EVENT_KIND_PM, cipheredMessage, [['p', recipientPubkey]], merchantPrivateKey);
    get(NostrPool).publish(relayUrlList, event).on('ok', successCB);
}

export async function getPrivateMessages(userPubkey: string, merchantPrivateKey:string | boolean = false, receivedCB, eoseCB = () => {}) {
    const sub = get(NostrPool).sub(relayUrlList, [
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
        let my_message_replying_to_this_pubkey: string | null = null;
        if (messagePubkey === userPubkey) {
            // Message sent by the userPubkey owner
            my_message_replying_to_this_pubkey = e.tags.find(([k, v]) => k === 'p' && v && v !== '')[1];
            decryptPubkey = my_message_replying_to_this_pubkey;         // My messages (output)
        } else {
            // Message received by the userPubkey owner
            decryptPubkey = messagePubkey;  // Replies
        }

        let decryptedContent;
        if (!merchantPrivateKey) {
            if (get(NostrLoginMethod) === 'extension' && hasExtension()) {
                try {
                    decryptedContent = await (window as any).nostr.nip04.decrypt(decryptPubkey, content);
                } catch (error) {
                    console.error("getPrivateMessages - Error decrypting a private message with the Nostr extension.");
                    return false;
                }
            } else {
                let privateKey = get(NostrPrivateKey);
                if (privateKey) {
                    try {
                        decryptedContent = await nip04.decrypt(privateKey, decryptPubkey, content);
                    } catch (error) {
                        console.error("getPrivateMessages - Error decrypting a private message with the private key of the logged-in user.");
                        return false;
                    }
                } else {
                    return false;
                }
            }
        } else {
            try {
                decryptedContent = await nip04.decrypt(merchantPrivateKey, decryptPubkey, content);
            } catch (error) {
                console.error("getPrivateMessages - Error decrypting a private message with the private key of the merchant.");
                return false;
            }
        }


        try {
            let jsonDecodedMessage = JSON.parse(decryptedContent);
            jsonDecodedMessage.created_at = e.created_at;
            jsonDecodedMessage.pubkey = messagePubkey;
            jsonDecodedMessage.contentType = 'json';

            try {
                receivedCB(jsonDecodedMessage);
            } catch (error) {
                console.error('------------------------------ Error calling getPrivateMessages callback for automatic (order) messages:', error);
            }
        } catch (error) {
            let humanMessage = {
                id: e.id,
                message: decryptedContent,
                created_at: e.created_at,
                pubkey: e.pubkey,
                contentType: 'human',
            };

            if (my_message_replying_to_this_pubkey) {
                humanMessage.my_message_replying_to_this_pubkey = my_message_replying_to_this_pubkey;
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
// Metadata (nip-1)
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

export function subscribeMetadata(pubkeys: string[], receivedCB: (pubkey: string, metadata: UserMetadata) => void, eoseCB: () => void) {
    const sub = get(NostrPool).sub(relayUrlList, [{ kinds: [Kind.Metadata], authors: pubkeys }]);
    sub.on('event', e => {
        try {
            let jsonDecodedMetadata = JSON.parse(e.content);
            jsonDecodedMetadata.created_at = e.created_at;
            jsonDecodedMetadata.pubkey = e.pubkey;
            jsonDecodedMetadata.tags = e.tags;
            receivedCB(e.pubkey, jsonDecodedMetadata);
        } catch (error) { }
    });
    if (eoseCB) {
        sub.on('eose', eoseCB);
    }
}

export async function publishMetadata(profile, tags, successCB: () => void) {
    // We put this on the profile for easier access, but cannot be
    // saved to the profile, so we remove them before publishing
    delete profile.created_at;
    delete profile.pubkey;
    delete profile.tags;

    const event = await createEvent(Kind.Metadata, JSON.stringify(profile), tags);

    get(NostrPool)
        .publish(relayUrlList, event)
        .on('ok', successCB);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// NostrMarket (nip-15)
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

    const sub: Sub = get(NostrPool).sub(relayUrlList, [filter]);
    sub.on('event', e => receivedCB(e));
    sub.on('eose', () => {
        // sub.unsub()
    })
}

export function getProducts(merchantPubkey: string | null, productIds: string[] | null, receivedCB: (e) => void) {
    let filter: Filter = { kinds: [EVENT_KIND_PRODUCT, EVENT_KIND_AUCTION] };

    if (merchantPubkey) {
        filter.authors = [merchantPubkey];
    }

    if (productIds) {
        filter['#d'] = productIds;
    }

    const sub: Sub = get(NostrPool).sub(relayUrlList, [filter]);
    sub.on('event', e => {receivedCB(e);});
    sub.on('eose', () => {
        // sub.unsub()
    })
}

/**
 * Used to subscribe to all the information about a specific auction
 */
export function subscribeAuction(listOfAuctionsToGetInfo, receivedCB: (event) => void, eoseCB) {
    const sub = get(NostrPool)
        .sub(relayUrlList, [{ kinds: [ EVENT_KIND_AUCTION_BID, EVENT_KIND_AUCTION_BID_STATUS ], '#e': listOfAuctionsToGetInfo }]);
    sub.on('event', receivedCB);
    if (eoseCB) {
        sub.on('eose', eoseCB);
    }
}

/**
 * Used to subscribe for all the auctions that I won
 */
export function subscribeWonAuctions(pubkey, receivedCB: (event) => void, eoseCB) {
    const expiryDays = 3;

    const sub = get(NostrPool)
        .sub(relayUrlList, [{
            kinds: [ EVENT_KIND_AUCTION_BID_STATUS ],
            '#p': [pubkey],
            since: Math.floor(Date.now() / 1000) - (expiryDays * 24 * 3600)
        }]);
    sub.on('event', receivedCB);
    if (eoseCB) {
        sub.on('eose', eoseCB);
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Badges (nip-58)
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

export function getProfileBadges(pubkey: string, receivedCB : (event) => void) {
    get(NostrPool)
        .sub(relayUrlList, [
            {
                kinds: [EVENT_KIND_PROFILE_BADGES],
                authors: [pubkey],
                '#d': ['profile_badges'],
                limit: 1
            }])
        .on('event', receivedCB);
}

export function getBadgeAward(pubkey: string, receivedCB : (event) => void) {
    get(NostrPool)
        .sub(relayUrlList, [
            {
                kinds: [EVENT_KIND_BADGE_AWARD],
                '#p': [pubkey]
            }])
        .on('event', receivedCB);
}

export function getBadgeDefinitions(badgeName: string, author: string, receivedCB : (event) => void) {
    get(NostrPool)
        .sub(relayUrlList, [
            {
                kinds: [EVENT_KIND_BADGE_DEFINITION],
                authors: [author],
                '#d': [badgeName]
            }])
        .on('event', receivedCB);
}

export async function nostrAcceptBadge(newProfileBadgeTags, successCB: () => void) {
    let callBackCalled = false;

    if (newProfileBadgeTags.length < 3) {
        console.error('Tags for Accepted badges for the profile must have at least 3 tags if you just added one');
        return;
    }

    const event = await createEvent(
        EVENT_KIND_PROFILE_BADGES,
        '',
        newProfileBadgeTags
    );
    get(NostrPool).publish(relayUrlList, event).on('ok', () => {
        if (successCB && !callBackCalled) {
            callBackCalled = true;
            successCB();
        }
    });
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Arbitrary custom app data (nip-78)
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

export function subscribeConfiguration(pubkeys: string[], receivedCB: (setup: string, createdAt: number) => void) {
    const sub = get(NostrPool).sub(
        relayUrlList,
        [
            {
                kinds: [EVENT_KIND_APP_SETUP],
                authors: pubkeys,
                '#p': [SITE_SPECIFIC_CONFIG_KEY],
            }
        ]
    );
    sub.on('event', e => receivedCB(JSON.parse(e.content), e.created_at));
}
