import { writable, type Writable } from 'svelte/store';
import type { User } from "./types/user";

export const token: Writable<string | null> = writable(null);

export const user: Writable<User | null> = writable(null);

export const Info: Writable<string | null | {message: string, duration: number, url: string, button: string}> = writable(null);
export const Error: Writable<string | null> = writable(null);

export const BTC2USD: Writable<number | null> = writable(null);
