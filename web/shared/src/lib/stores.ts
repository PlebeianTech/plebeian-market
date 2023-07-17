import { writable, type Writable } from 'svelte/store';

export const loginModalState: Writable<{
    openRequested: boolean;
    callbackFunc: () => void;
}> = writable({
    openRequested: false,
    callbackFunc: () => {}
});

export const NostrPublicKey: Writable<string | null> = writable(null);
export const NostrPrivateKey: Writable<string | null> = writable(null);

// Human messages are indexed by publicKey
// Automatic messages (orders) are indexed by orderId
export const privateMessages: Writable<{
    human: [],
    automatic: []
}> = writable({
    human: [],
    automatic: []
});
