export interface IAccount {
    nym: string | null;
    displayName: string | null;
    profileImageUrl: string | null;
    email: string | null;
    emailVerified: boolean;
    telegramUsername: string | null;
    telegramUsernameVerified: boolean;
    twitterUsername: string | null;
    twitterUsernameVerified: boolean;
}

export class User implements IAccount {
    nym: string | null = null;
    displayName: string | null = null;
    profileImageUrl: string | null = null;
    email: string | null = null;
    emailVerified: boolean = false;
    telegramUsername: string | null = null;
    telegramUsernameVerified: boolean = false;
    twitterUsername: string | null = null;
    twitterUsernameVerified: boolean = false;
    twitterVerificationPhraseSentAt: Date | null = null;
    stallBannerUrl: string | null = null;
    stallName: string | null = null;
    stallDescription: string | null = null;
    contributionPercent: number | null = null;
    xpub: string | null = null;
    hasItems: boolean = false;
    hasOwnItems: boolean = false;
    hasActiveAuctions: boolean = false;
    hasPastAuctions: boolean = false;
    hasActiveListings: boolean = false;
    hasPastListings: boolean = false;
    isModerator: boolean = false;
}

export function fromJson(json: any): User {
    return {
        nym: <string | null>json.nym,
        displayName: <string | null>json.display_name,
        profileImageUrl: <string | null>json.profile_image_url,
        email: <string | null>json.email,
        emailVerified: <boolean>json.email_verified,
        telegramUsername: <string | null>json.telegram_username,
        telegramUsernameVerified: <boolean>json.telegram_username_verified,
        twitterUsername: <string | null>json.twitter_username,
        twitterUsernameVerified: <boolean>json.twitter_username_verified,
        twitterVerificationPhraseSentAt: json.twitter_verification_phrase_sent_at ? new Date(json.twitter_verification_phrase_sent_at) : null,
        stallBannerUrl: <string | null>json.stall_banner_url,
        stallName: <string | null>json.stall_name,
        stallDescription: <string | null>json.stall_description,
        hasItems: <boolean>json.has_items,
        hasOwnItems: <boolean>json.has_own_items,
        hasActiveAuctions: <boolean>json.has_active_auctions,
        hasPastAuctions: <boolean>json.has_past_auctions,
        hasActiveListings: <boolean>json.has_active_listings,
        hasPastListings: <boolean>json.has_past_listings,
        contributionPercent: <number | null>json.contribution_percent,
        xpub: <string | null>json.xpub,
        isModerator: <boolean>json.is_moderator,
    }
}
