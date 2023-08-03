import { writable, type Writable } from 'svelte/store';
import type { User } from "$lib/types/user";

export const user: Writable<User | null> = writable(null);

export enum AuthBehavior {
    Login = "login",
}

export type AuthCallback = () => void;

export type AuthOptions = {
    default?: AuthBehavior,
    cb?: AuthCallback,
}

export const AuthRequired: Writable<AuthOptions | true | false> = writable(false);
