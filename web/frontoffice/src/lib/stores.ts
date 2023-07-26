import { writable, type Writable } from 'svelte/store';
import { SimplePool } from 'nostr-tools';

export type Placement = 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'top-center' | 'bottom-center' | 'center-center';

export const BTC2USD: Writable<number | null> = writable(null);

export const NostrPool: Writable<SimplePool> = writable(new SimplePool());

export const stalls: Writable<{
    stalls: object,
    fetched_at: number
} | null> = writable({
    stalls: {},
    fetched_at: 0
});

export const products: Writable<{
    products: object,
    fetched_at: number
} | null> = writable(null);

interface CategoriesInfo {
    amount: number,
    selected: boolean
}

export const productCategories: Writable<CategoriesInfo[] | null> = writable(null);

export const NostrGlobalConfig: Writable<object> = writable({});
