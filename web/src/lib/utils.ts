export function isLocal() {
    return window.location.href.indexOf("localhost") !== -1 || window.location.href.indexOf("127.0.0.1") !== -1 || window.location.href.indexOf("0.0.0.0") !== -1;
}

export function isStaging() {
    return window.location.href.indexOf("staging") !== -1;
}

export function sats2usd(sats: number, btc2usd: number | null): number | null {
    if (btc2usd === null) {
        return null;
    } else {
        return sats / 100000000 * btc2usd;
    }
}
