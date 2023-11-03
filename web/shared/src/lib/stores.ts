import { writable, type Writable } from 'svelte/store';
import type {ShoppingCartItem} from "./types/stall";
import {SimplePool} from "nostr-tools";

export type Placement = 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'top-center' | 'bottom-center' | 'center-center';

export const Info: Writable<string | null | {message: string, duration: number, url: string, button: string, placement: Placement}> = writable(null);
export const Error: Writable<string | null> = writable(null);

export const token: Writable<string | null> = writable(null);

export const BTC2USD: Writable<number | null> = writable(null);

export const currentFiatCurrency: Writable<string | null> = writable(null);
export const fiatRates: Writable<Map<string, object>> = writable(new Map());

export const loginModalState: Writable<{
    openRequested: boolean;
    loginSuccessCB: () => void;
    loginBackofficeSuccessCB: () => void;
}> = writable({
    openRequested: false,
    loginSuccessCB: () => {},
    loginBackofficeSuccessCB: () => {},
});

export const NostrPool: Writable<SimplePool> = writable(new SimplePool());
export const NostrPublicKey: Writable<string | null> = writable(null);
export const NostrPrivateKey: Writable<string | null> = writable(null);
export const NostrLoginMethod: Writable<string | null> = writable(null);

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
} | null> = writable({
    stalls: {},
    fetched_at: 0
});

// Human messages are indexed by publicKey
// Automatic messages (orders) are indexed by orderId
export const privateMessages: Writable<{
    human: [],
    automatic: []
}> = writable({
    human: [],
    automatic: []
});
