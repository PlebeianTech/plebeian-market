import {goto} from "$app/navigation";
//import {Info,  privateMessages} from "$lib/stores";
import {NostrPublicKey, loginModalState} from "$sharedLib/stores";
import {get} from "svelte/store";

export const SATS_IN_BTC = 100000000;

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

export function requestLoginModal(callbackFunc: () => void = () => {}) {
    loginModalState.set({
        openRequested: true,
        callbackFunc
    });
}

export async function waitAndShowLoginIfNotLoggedAlready() {
    await new Promise(resolve => setTimeout(resolve, 300));
    if (!get(NostrPublicKey)) {
        requestLoginModal();
        return false;
    }
    return true;
}

export function logout(gotoUrl?: string) {
    NostrPublicKey.set(null);
/*
    privateMessages.set({
        human: [],
        automatic: []
    });
*/
    localStorage.removeItem('nostrPublicKey');
    localStorage.removeItem('readMessages');

//    Info.set("You're Logged out");

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

export function getMonthName(month: number) {
    let firstOfThatMonth = new Date(new Date().getFullYear(), month - 1 /* months start from 0 in javascript */, 1);
    return firstOfThatMonth.toLocaleString('default', { month: 'long' });
}

export async function getConfigurationFromFile() {
    let response = await fetch('config.json')

    if (!response.ok) {
        return false;
    }

    try {
        return await response.json();
    } catch (e) {
        console.debug('ERROR', e);
        return false;
    }
}
