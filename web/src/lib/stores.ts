import { writable, type Writable } from 'svelte/store';
import type { User } from "./types/user";

export const token: Writable<string | null> = writable(null);

export const user: Writable<User | null> = writable(null);

export const Info: Writable<string | null> = writable(null);
