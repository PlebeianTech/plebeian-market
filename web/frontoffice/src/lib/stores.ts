import { writable, type Writable } from 'svelte/store';

export const BTC2USD: Writable<number | null> = writable(null);

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
