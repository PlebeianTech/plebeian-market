export interface IAccount {
    username: string | null;
    usernameVerified: boolean;
    profileImageUrl: string | null;
}

export interface User {
    nym: string;
    twitter: IAccount;
    twitterUsernameVerificationTweet: string | null;
    contributionPercent: number | null;
    xpub: string | null;
    hasItems: boolean;
    hasListings: boolean;
    hasBids: boolean;
    isModerator: boolean;
    runningAuctionCount: number;
    endedAuctionCount: number;
}

export function fromJson(json: any): User {
    return {
        nym: <string>json.nym,
        twitter: {
            username: <string | null>json.twitter_username,
            profileImageUrl: <string | null>json.twitter_profile_image_url,
            usernameVerified: <boolean>json.twitter_username_verified,
        },
        twitterUsernameVerificationTweet: <string | null>json.twitter_username_verification_tweet,
        contributionPercent: <number | null>json.contribution_percent,
        xpub: <string | null>json.xpub,
        hasItems: <boolean>json.has_items,
        hasListings: <boolean>json.has_listings,
        hasBids: <boolean>json.has_bids,
        isModerator: <boolean>json.is_moderator,
        runningAuctionCount: <number>json.running_auction_count,
        endedAuctionCount: <number>json.ended_auction_count,
    }
}
