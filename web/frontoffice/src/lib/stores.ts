import { writable, type Writable } from 'svelte/store';

interface CategoriesInfo {
    amount: number,
    selected: boolean
}

export const productCategories: Writable<CategoriesInfo[] | null> = writable(null);
