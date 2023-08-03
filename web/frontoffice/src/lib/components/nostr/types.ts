import type { Event } from 'nostr-tools';
import type { UserMetadata } from "$sharedLib/services/nostr";

export type VitaminedMessage = Event & {
    reactions?: Map<string, Set<string>>,
    samePubKey?: boolean,
    profile?: UserMetadata,
    nip05VerifiedAddress?: string,
    repliedToMessage?: VitaminedMessage,
    replies?: string[];
    imagePreviewUrl?: string,
};
