import {getValue} from "btc2fiat";
import {get} from "svelte/store";
import {fiatRates} from "$sharedLib/stores";

export const currencyRateCacheTimeMilliseconds = 1000 * 60 * 10; // 10 minutes

// https://en.wikipedia.org/wiki/Currency
export const supportedFiatCurrencies = [
    {
        symbol: 'USD',
        name: 'US Dollar',
        prefix: '$',
        suffix: ''
    },
    {
        symbol: 'EUR',
        name: 'Euro',
        prefix: '',
        suffix: ' €'
    },
    {
        symbol: 'GBP',
        name: 'GBP',
        prefix: '£',
        suffix: ''
    },
    {
        symbol: 'JPY',
        name: 'Yen',
        prefix: '¥',
        suffix: ''
    },
    {
        symbol: 'CAD',
        name: 'Canadian Dollar',
        prefix: 'C$',
        suffix: ''
    },
    /*
    {
        symbol: 'AUD',
        name: 'Australian Dollar',
        prefix: 'A$',
        suffix: ''
    },
    {
        symbol: 'CNY',
        name: 'Renmimbi',
        prefix: '¥',
        suffix: ''
    },
    {
        symbol: 'CHF',
        name: 'Swiss Franc',
        prefix: 'CHF',
        suffix: ''
    },
     */
];

export function getFiatCurrencyInfo(currentFiatCurrency: string) {
    return supportedFiatCurrencies.find((x) => x.symbol === currentFiatCurrency);
}

export async function getFiatRate(fiatSymbol: string) {
    if (!fiatSymbol) {
        return;
    }

    let fiatRatesCache: Map<string, object> = get(fiatRates);

    let fiatRate = fiatRatesCache.get(fiatSymbol);

    if (!fiatRate || (fiatRate && fiatRate.fetched_at < (Date.now() - currencyRateCacheTimeMilliseconds))) {
        const rate: number = await getValue('kraken', fiatSymbol);

        if (!fiatRate) {
            fiatRatesCache.set(fiatSymbol, {
                rate: rate,
                fetched_at: Date.now()
            });
        } else {
            fiatRate.rate = rate;
            fiatRate.fetched_at = Date.now();
        }

        // Fire Svelte reactivity
        fiatRates.set(get(fiatRates));
    }
}
