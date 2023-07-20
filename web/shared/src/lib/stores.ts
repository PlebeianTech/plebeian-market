import { writable, type Writable } from 'svelte/store';

export const Info: Writable<string | null | {message: string, duration: number, url: string, button: string, placement: Placement}> = writable(null);
export const Error: Writable<string | null> = writable(null);

export const loginModalState: Writable<{
    openRequested: boolean;
    loginSuccessCB: () => void;
    loginBackofficeSuccessCB: () => void;
}> = writable({
    openRequested: false,
    loginSuccessCB: () => {},
    loginBackofficeSuccessCB: () => {},
});

export const NostrPublicKey: Writable<string | null> = writable(null);
export const NostrPrivateKey: Writable<string | null> = writable(null);
export const NostrLoginMethod: Writable<string | null> = writable(null);

// Human messages are indexed by publicKey
// Automatic messages (orders) are indexed by orderId
export const privateMessages: Writable<{
    human: [],
    automatic: []
}> = writable({
    human: [],
    automatic: []
});
