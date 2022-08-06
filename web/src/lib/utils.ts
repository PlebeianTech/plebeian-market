import { browser } from "$app/env";

export function isLocal() {
    // TODO: deal with local network addresses
    // alternatively: pass an environment variable from the Dockerfile to node.js, in the same way we pass BASE_URL for the Python API => no more guessing based on the URL
    if ( browser ) {
        return window.location.href.indexOf("localhost") !== -1 || window.location.href.indexOf("127.0.0.1") !== -1 || window.location.href.indexOf("0.0.0.0") !== -1;
    }
    return false;
}

export function isStaging() {
    if ( browser ) {
        return window.location.href.indexOf("staging") !== -1;
    }
    return false;
}

export function getBaseUrl() {
    if (isLocal()) {
        return "http://localhost:3000/";
    } else if (isStaging()) {
        return "https://staging.plebeian.market/";
    } else {
        return "https://plebeian.market/";
    }
}


// TODO: I think we need to add a new .env file
// for Vite which allows us to tell the difference between
// each environment we are on - I don't know the current
// server config so do want to mess with this too much
export function getBaseApiUrl() {
    let mode = import.meta.env.MODE;
    if (mode === "development") {
        return 'http://localhost:5000';
    }
    if (mode === "staging") {
        return 'https://staging.plebeian.market';
    }
    return 'https://plebeian.market';
}

export function sats2usd(sats: number, btc2usd: number | null): number | null {
    if (btc2usd === null) {
        return null;
    } else {
        return sats / 100000000 * btc2usd;
    }
}

export function getDomain() {
    if (isLocal()) {
        return "localhost:3000";
    } else if (isStaging()) {
        return "staging.plebeian.market";
    } else {
        return "plebeian.market";
    }
}
