import { writable, type Writable } from 'svelte/store';

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
