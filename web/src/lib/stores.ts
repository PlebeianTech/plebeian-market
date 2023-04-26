import { writable, type Writable } from 'svelte/store';
import { SimplePool } from 'nostr-tools';
import type { User } from "$lib/types/user";
import {ShoppingCart, ShoppingCartItem} from "./types/stall";

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

export const NostrPool: Writable<SimplePool> = writable(new SimplePool());

export enum NostrKeySource {
    PlebeianMarketUser = "your Plebeian Market account",
    Extension = "your browser extension",
}
export const NostrPublicKey: Writable<{source: NostrKeySource, key: string | null}> = writable({source: NostrKeySource.PlebeianMarketUser, key: null});

export type ShoppingCartSummary = {
    numProducts: number,
    totalQuantity: number,
    stalls: number
}
type stallId = string;
type productId = string;

export const ShoppingCart: Writable<{
    products: Map<stallId, Map<productId, ShoppingCartItem>>,
    summary: ShoppingCartSummary
}> = writable({
    products: new Map(),
    summary: {
        numProducts: 0,
        totalQuantity: 0,
        stalls: 0
    }
});

export const stalls: Writable<{
    stalls: object,
    fetched_at: number
} | null> = writable(null);

export const products: Writable<{
    products: object,
    fetched_at: number
} | null> = writable(null);
