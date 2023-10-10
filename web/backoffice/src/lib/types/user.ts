export interface IAccount {
    nym: string | null;
    displayName: string | null;
    email: string | null;
    emailVerified: boolean;
    telegramUsername: string | null;
    telegramUsernameVerified: boolean;
    twitterUsername: string | null;
    twitterUsernameVerified: boolean;
    nostrPublicKey: string | null;
}

export enum ExternalAccountProvider {
    Email = 'email',
}

export class User implements IAccount {
    identity: string = '';
    hasLnauthKey: boolean = false;
    lnauthKeyName: string | null = null;
    nostrPublicKey: string | null = null;
    nym: string | null = null;
    displayName: string | null = null;
    email: string | null = null;
    emailVerified: boolean = false;
    emailVerificationPhraseSentAt: Date | null = null;
    telegramUsername: string | null = null;
    telegramUsernameVerified: boolean = false;
    twitterUsername: string | null = null;
    twitterUsernameVerified: boolean = false;
    stallBannerUrl: string | null = null;
    stallName: string | null = null;
    stallDescription: string | null = null;
    shippingFrom: string | null = null;
    shippingDomesticUsd: number | null = null;
    shippingWorldwideUsd: number | null = null;
    contributionPercent: number | null = null;
    wallet: string | null = null;
    walletName: string | null = null;
    lightningAddress: string | null = null;
    hasItems: boolean = false;
    hasOwnItems: boolean = false;
    hasActiveAuctions: boolean = false;
    hasPastAuctions: boolean = false;
    hasActiveListings: boolean = false;
    hasPastListings: boolean = false;
}

export function fromJson(json: any): User {
    var u = new User();
    u.identity = <string>json.identity;
    u.hasLnauthKey = <boolean>json.has_lnauth_key;
    u.lnauthKeyName = <string | null>json.lnauth_key_name;
    u.nostrPublicKey = <string | null>json.nostr_public_key;
    u.nym = <string | null>json.nym;
    u.displayName = <string | null>json.display_name;
    u.email = <string | null>json.email;
    u.emailVerified = <boolean>json.email_verified;
    u.emailVerificationPhraseSentAt = json.email_verification_phrase_sent_at ? new Date(json.email_verification_phrase_sent_at) : null;
    u.telegramUsername = <string | null>json.telegram_username;
    u.telegramUsernameVerified = <boolean>json.telegram_username_verified;
    u.twitterUsername = <string | null>json.twitter_username;
    u.twitterUsernameVerified = <boolean>json.twitter_username_verified;
    u.stallBannerUrl = <string | null>json.stall_banner_url;
    u.stallName = <string | null>json.stall_name;
    u.stallDescription = <string | null>json.stall_description;
    u.shippingFrom = <string | null>json.shipping_from;
    u.shippingDomesticUsd = <number | null>json.shipping_domestic_usd;
    u.shippingWorldwideUsd = <number | null>json.shipping_worldwide_usd;
    u.hasItems = <boolean>json.has_items;
    u.hasOwnItems = <boolean>json.has_own_items;
    u.hasActiveAuctions = <boolean>json.has_active_auctions;
    u.hasPastAuctions = <boolean>json.has_past_auctions;
    u.hasActiveListings = <boolean>json.has_active_listings;
    u.hasPastListings = <boolean>json.has_past_listings;
    u.contributionPercent = <number | null>json.contribution_percent;
    u.wallet = <string | null>json.wallet;
    u.walletName = <string | null>json.wallet_name;
    u.lightningAddress = <string | null>json.lightning_address;

    return u;
}
