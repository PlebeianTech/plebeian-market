import {goto} from "$app/navigation";
import {NostrPublicKey, NostrLoginMethod, loginModalState, Info, isSuperAdmin, privateMessages, ShoppingCart, token} from "$sharedLib/stores";
import {get} from "svelte/store";
import {browser} from "$app/environment";
import {page} from "$app/stores";

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

export function requestLoginModal(loginSuccessCB: () => void = () => {}, loginBackofficeSuccessCB: () => void = () => {}) {
    loginModalState.set({
        openRequested: true,
        loginSuccessCB,
        loginBackofficeSuccessCB,
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

export function cleanShoppingCart() {
    ShoppingCart.set({
        products: new Map(),
        summary: {
            numProducts: 0,
            totalQuantity: 0,
            stalls: 0
        }
    });

    localStorage.removeItem('shoppingCartProducts');
}

export function logout(gotoUrl?: string) {
    Info.set("You're Logged out");

    NostrPublicKey.set(null);
    isSuperAdmin.set(false);

    privateMessages.set({
        human: [],
        automatic: []
    });

    cleanShoppingCart();

    if (browser) {
        // Frontstore
        localStorage.removeItem('nostrPublicKey');
        localStorage.removeItem('nostrLoginMethod');

        // Backstore
        localStorage.removeItem('token');
    }

    token.set(null);

    if (gotoUrl !== undefined) {
        goto(gotoUrl);
    } else {
        goto('/');
    }
}

export function setLoginMethod(method: string): void {
    if (browser) {
        NostrLoginMethod.set(method);
        localStorage.setItem('nostrLoginMethod', method);
    }
}

export function loggedIn(): boolean {
    return get(NostrLoginMethod) !== null;
}

export function getDomainName() {
    const urlParts = get(page).url.href.split("/");
    return urlParts[2] ?? null;
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
    // TODO Improve this
    // return {
    //     "admin_pubkeys": [
    //       "6e8f172de9b5f21b45c80f4bbd6989110914a816517e7d09eb2ddcef050b014b"
    //     ],
    //     "homepage_banner_image": "",
    //     "backend_present": false
    //   }
      
    let response = await fetch('/config.json')

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
