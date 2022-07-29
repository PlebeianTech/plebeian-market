export interface IAccount {
    username: string;
    usernameVerified: boolean;
    profileImageUrl: string;
}

export interface User {
    contributionPercent: number;
    twitterUsername: string;
    twitterProfileImageUrl: string;
    twitterUsernameVerified: boolean;
    twitterUsernameVerificationTweet: string;
    hasAuctions: boolean;
    hasBids: boolean;
    isModerator: boolean;
    activeAuctionCount: number;
    pastAuctionCount: number;
    storeName: string;
    storeDescription: string;
}

export function fromJson(json: any) {
    return {
        contributionPercent: <number>json.contribution_percent,
        twitterUsername: <string>json.twitter_username,
        twitterProfileImageUrl: <string>json.twitter_profile_image_url,
        twitterUsernameVerified: <boolean>json.twitter_username_verified,
        twitterUsernameVerificationTweet: <string>json.twitter_username_verification_tweet,
        hasAuctions: <boolean>json.has_auctions,
        hasBids: <boolean>json.has_bids,
        isModerator: <boolean>json.is_moderator,
        activeAuctionCount: <number>json.active_auction_count,
        pastAuctionCount: <number>json.past_auction_count,
        storeName: <string>json.store_name,
        storeDescription: <string>json.store_description
    }
}
