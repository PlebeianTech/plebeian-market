import {getValue} from "btc2fiat";
import {get} from "svelte/store";
import {fiatRates, userChosenCurrency} from "$sharedLib/stores";
import {SATS_IN_BTC} from "$sharedLib/utils";

export const currencyRateCacheTimeMilliseconds = 1000 * 60 * 10; // 10 minutes

// https://en.wikipedia.org/wiki/Currency
export const supportedCurrencies = [
    {
        symbol: 'SAT',
        name: 'Bitcoin (Satoshis)',
        prefix: '',
        suffix: ' sats'
    },
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

export function getCurrencyInfo(currency: string) {
    return supportedCurrencies.find((x) => x.symbol === currency);
}

export async function getFiatRate(fiatSymbol: string) {
    fiatSymbol = getStandardCurrencyCode(fiatSymbol);

    if (!fiatSymbol || fiatSymbol === 'SAT') {
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

export function getStandardCurrencyCode(currencyCode: string) {
    if (['sat', 'SAT', 'sats', 'SATS'].includes(currencyCode)) {
        return 'SAT';
    }

    return currencyCode;
}

export async function convertCurrencies(amount: number, sourceCurrency: string) {
    let satsIntermediateAmount;
    let convertedAmount;

    sourceCurrency = getStandardCurrencyCode(sourceCurrency);

    // Step 1: convert source currency to sats
    if (sourceCurrency === 'SAT') {
        satsIntermediateAmount = amount;
    } else {
        await getFiatRate(sourceCurrency);

        const sourceCurrencyFiatRate = get(fiatRates).get(sourceCurrency).rate;

        satsIntermediateAmount = amount * SATS_IN_BTC / sourceCurrencyFiatRate;
    }

    if (sourceCurrency === get(userChosenCurrency)) {
        return {
            sourceAmount: amount,
            sourceCurrency: sourceCurrency,
            amount: amount,
            currency: get(userChosenCurrency),
            sats: Number(removeDecimals(satsIntermediateAmount, 'SAT'))
        };
    }

    // Step 2: convert sats to destination currency
    if (get(userChosenCurrency) === 'SAT') {
        convertedAmount = satsIntermediateAmount;
    } else {
        await getFiatRate(get(userChosenCurrency));
        const destinationCurrencyFiatRate = get(fiatRates).get(get(userChosenCurrency)).rate;

        convertedAmount = satsIntermediateAmount * destinationCurrencyFiatRate / SATS_IN_BTC;
    }

    return {
        sourceAmount: amount,
        sourceCurrency: sourceCurrency,
        amount: Number(removeDecimals(convertedAmount)),
        currency: get(userChosenCurrency),
        sats: Number(removeDecimals(satsIntermediateAmount, 'SAT'))
    };
}

export function removeDecimals(amount, currency: string = get(userChosenCurrency)):number {
    if (currency && currency === 'SAT') {
        return amount.toFixed(0);
    }

    if (!isNaN(amount)) {
        if (amount > 1) {
            amount = amount.toFixed(2);
        } else if (amount > 99) {
            amount = amount.toFixed(0);
        } else {
            amount = amount.toFixed(4);
        }
    }

    return amount;
}
