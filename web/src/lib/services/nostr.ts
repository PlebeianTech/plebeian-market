import {getEventHash, Kind, SimplePool} from 'nostr-tools';
import type {Sub} from "nostr-tools";
import { UserResume } from "$lib/types/user";
import { relayUrlList } from "$lib/nostr/utils";

const EVENT_KIND_RESUME = 66;

async function createEvent(kind: number, content: any) {
    let event: any = {
        kind,
        content,
        tags: [],
        created_at: Math.floor(Date.now() / 1000),
    }

    event.pubkey = await window.nostr.getPublicKey();
    event.id = getEventHash(event);
    return await window.nostr.signEvent(event);
}

export async function closePool(pool: SimplePool) {
    await pool.close(relayUrlList);
}

export function subscribeResumes(pool: SimplePool, receivedCB: (pubkey: string, resume: UserResume, createdAt: number) => void) {
    let sub: Sub = pool.sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME] }]);
    sub.on('event', e => receivedCB(e.pubkey, UserResume.fromJson(JSON.parse(e.content)), e.created_at));
    sub.on('eose', () => {
        sub.unsub()
    })
}

export function subscribeResume(pool: SimplePool, pubkey: string, receivedCB: (resume: UserResume, createdAt: number) => void) {
    let sub: Sub = pool.sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME], authors: [pubkey] }]);
    sub.on('event', e => receivedCB(UserResume.fromJson(JSON.parse(e.content)), e.created_at));
    sub.on('eose', () => {
        sub.unsub()
    })
}

export async function publishResume(pool: SimplePool, resume: UserResume, successCB: () => void) {
    const event = await createEvent(EVENT_KIND_RESUME, JSON.stringify(resume.toJson()));
    for (const pub of pool.publish(relayUrlList, event)) {
        pub.on('ok', successCB);
    }
}

export function subscribeMetadata(pool: SimplePool, pubkeys: string[], receivedCB: (pubkey: string, metadata: {name: string, picture: string, about: string}) => void) {
    let sub: Sub = pool.sub(relayUrlList, [{ kinds: [Kind.Metadata], authors: pubkeys }]);
    sub.on('event', e => {receivedCB(e.pubkey, JSON.parse(e.content))});
    sub.on('eose', () => {
        sub.unsub()
    });
}

export function subscribeToChannel(pool: SimplePool, nostrRoomId, messageLimit, since, receivedCB): Sub {
    let sub: Sub = pool.sub(relayUrlList, [{
        kinds: [Kind.ChannelMessage],
        '#e': [nostrRoomId],
        limit: messageLimit,
        since: since
    }]);

    sub.on('event', event => { receivedCB(event); });

    return sub;
}

export function subscribeToReactions(pool: SimplePool, listOfNotesToGetInfo, receivedCB): Sub {
    let sub: Sub = pool.sub(relayUrlList, [{
        kinds: [
            Kind.Text,
            Kind.Reaction
        ],
        '#e': listOfNotesToGetInfo
    }]);

    sub.on('event', event => { receivedCB(event); });

    return sub;
}
