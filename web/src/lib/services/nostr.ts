import { getEventHash, Kind, SimplePool} from 'nostr-tools';
import { UserResume, type User } from "$lib/types/user";
import { relayUrlList } from "$lib/nostr/utils";

const EVENT_KIND_RESUME = 66;

async function createEvent(kind: number, content: any, user: User | null = null) {
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
    let sub = pool.sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME] }]);
    sub.on('event', e => receivedCB(e.pubkey, UserResume.fromJson(JSON.parse(e.content)), e.created_at));
}

export function subscribeResume(pool: SimplePool, pubkey: string, receivedCB: (resume: UserResume, createdAt: number) => void) {
    let sub = pool.sub(relayUrlList, [{ kinds: [EVENT_KIND_RESUME], authors: [pubkey] }]);
    sub.on('event', e => receivedCB(UserResume.fromJson(JSON.parse(e.content)), e.created_at));
}

export async function publishResume(pool: SimplePool, resume: UserResume, successCB: () => void) {
    const event = await createEvent(EVENT_KIND_RESUME, JSON.stringify(resume.toJson()));
    for (const pub of pool.publish(relayUrlList, event)) {
        pub.on('ok', successCB);
    }
}

export function subscribeMetadata(pool: SimplePool, pubkeys: string[], receivedCB: (pubkey: string, metadata: {name: string, picture: string, about: string}) => void) {
    let sub = pool.sub(relayUrlList, [{ kinds: [Kind.Metadata], authors: pubkeys }]);
    sub.on('event', e => receivedCB(e.pubkey, JSON.parse(e.content)));
}

export async function getProfileInfo(pool: SimplePool, userPubKey: string, receivedCB: (profileInfo) => void) {
    let profileInfoEvent = await pool.get(relayUrlList, {
        kinds: [Kind.Metadata],
        authors: [userPubKey]
    });

    if (profileInfoEvent !== null) {
        const profileContentJSON = profileInfoEvent.content;

        if (profileContentJSON) {
            receivedCB(JSON.parse(profileContentJSON));
        }
    }
}
