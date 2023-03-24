import { writable, type Writable } from 'svelte/store';
import type { User } from "./types/user";
import type { NostrUser } from "./types/nostrUser";
import {SimplePool} from "nostr-tools";

export const token: Writable<string | null> = writable(null);

export const user: Writable<User | null> = writable(null);

export type Placement = 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'top-center' | 'bottom-center' | 'center-center';

export const Info: Writable<string | null | {message: string, duration: number, url: string, button: string, placement: Placement}> = writable(null);
export const Error: Writable<string | null> = writable(null);

export const BTC2USD: Writable<number | null> = writable(null);

export const loginModalState: Writable<{
    openRequested: boolean;
    callbackFunc: () => void;
}> = writable({
    openRequested: false,
    callbackFunc: () => {}
});

export const nostrUser: Writable<NostrUser | null> = writable(null);

export const nostrPool: Writable<SimplePool> = writable(new SimplePool());
