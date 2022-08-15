export function isLocal() {
    // TODO: deal with local network addresses
    // alternatively: pass an environment variable from the Dockerfile to node.js, in the same way we pass BASE_URL for the Python API => no more guessing based on the URL
    return window.location.href.indexOf("localhost") !== -1 || window.location.href.indexOf("127.0.0.1") !== -1 || window.location.href.indexOf("0.0.0.0") !== -1;
}

export function isStaging() {
    return window.location.href.indexOf("staging") !== -1;
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

export function getEnvironmentInfo() {
    if (isLocal()) {
        return "local";
    } else if (isStaging()) {
        return "staging";
    } else {
        return "";
    }
}

export function sats2usd(sats: number, btc2usd: number | null): number | null {
    if (btc2usd === null) {
        return null;
    } else {
        return sats / 100000000 * btc2usd;
    }
}
