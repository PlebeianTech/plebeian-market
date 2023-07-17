import {browser} from "$app/environment";
import {goto} from "$app/navigation";
import { AuthRequired, AuthBehavior, token, Info } from "$lib/stores";

export let SATS_IN_BTC = 100000000;
export let SHORT_TITLE_LIMIT = 70;
export let SHORT_DESCRIPTION_LIMIT = 200;

export function isDevelopment() {
    return import.meta.env.MODE === 'development';
}

export function isStaging() {
    return import.meta.env.MODE === 'staging';
}

export function isProduction() {
    return import.meta.env.MODE === 'production';
}

export function getBaseUrl() {
    return import.meta.env.VITE_BASE_URL;
}

export function getApiBaseUrl() {
    return import.meta.env.VITE_API_BASE_URL;
}

export function getEnvironmentInfo() {
    return import.meta.env.MODE;
}

export function login() {
    AuthRequired.set({default: AuthBehavior.Login});
}

export function logout(gotoUrl?: string) {
    token.set(null);

    if (browser) {
        localStorage.removeItem('token');
    }

    Info.set("You're Logged out");

    if (gotoUrl !== undefined) {
        goto(gotoUrl);
    }
}

export function sats2usd(sats: number, btc2usd: number | null): number | null {
    if (btc2usd === null) {
        return null;
    } else {
        return sats / SATS_IN_BTC * btc2usd;
    }
}

export function usd2sats(usd: number, btc2usd: number | null): number | null {
    if (btc2usd === null) {
        return null;
    } else {
        return usd / btc2usd * SATS_IN_BTC;
    }
}

export function formatBTC(sats: number) {
    return (1 / SATS_IN_BTC * sats).toFixed(9);
}

export function getShortTitle(longTitle): string {
    if (longTitle) {
        return longTitle.substring(0, SHORT_TITLE_LIMIT);
    }

    return '';
}

export function getShortDescription(longDescription): string {
    if (longDescription) {
        return longDescription.substring(0, SHORT_DESCRIPTION_LIMIT);
    }

    return '';
}

export function getMonthName(month: number) {
    let firstOfThatMonth = new Date(new Date().getFullYear(), month - 1 /* months start from 0 in javascript */, 1);
    return firstOfThatMonth.toLocaleString('default', { month: 'long' });
}
