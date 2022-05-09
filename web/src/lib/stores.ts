import { writable, type Writable } from 'svelte/store';

export const token: Writable<string | null> = writable(null);

export const ContributionPercent: Writable<number | null>  = writable(null);

export const TwitterUsername: Writable<string | null> = writable(null);
export const TwitterUsernameVerified: Writable<boolean | null>  = writable(null);

export const Info: Writable<string | null> = writable(null);
