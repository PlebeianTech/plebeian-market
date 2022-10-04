export interface IAccount {
    nym: string | null;
    profileImageUrl: string | null;
    twitterUsername: string | null;
    twitterUsernameVerified: boolean;
}

export class User implements IAccount {
    nym: string | null = null;
    profileImageUrl: string | null = null;
    twitterUsername: string | null = null;
    twitterUsernameVerified: boolean = false;
    stallBannerUrl: string | null = null;
    stallName: string | null = null;
    stallDescription: string | null = null;
    twitterUsernameVerificationTweet: string | null = null;
    contributionPercent: number | null = null;
    xpub: string | null = null;
    hasItems: boolean = false;
    hasAuctions: boolean = false;
    hasListings: boolean = false;
    isModerator: boolean = false;
}

export function fromJson(json: any): User {
    return {
        nym: <string | null>json.nym,
        profileImageUrl: <string | null>json.profile_image_url,
        twitterUsername: <string | null>json.twitter_username,
        twitterUsernameVerified: <boolean>json.twitter_username_verified,
        stallBannerUrl: <string | null>json.stall_banner_url,
        stallName: <string | null>json.stall_name,
        stallDescription: <string | null>json.stall_description,
        hasItems: <boolean>json.has_items,
        hasAuctions: <boolean>json.has_auctions,
        hasListings: <boolean>json.has_listings,
        contributionPercent: <number | null>json.contribution_percent,
        xpub: <string | null>json.xpub,
        twitterUsernameVerificationTweet: <string | null>json.twitter_username_verification_tweet,
        isModerator: <boolean>json.is_moderator,
    }
}
