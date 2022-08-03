export interface IAccount {
    username: string;
    usernameVerified: boolean;
    profileImageUrl: string;
}

export interface User {
    contributionPercent: number;
    twitterUsername: string;
    nym: string;
    twitterProfileImageUrl: string;
    twitterUsernameVerified: boolean;
    twitterUsernameVerificationTweet: string;
    hasAuctions: boolean;
    hasBids: boolean;
    isModerator: boolean;
    runningAuctionCount: number;
    endedAuctionCount: number;
}

export function fromJson(json: any) {
    return {
        contributionPercent: <number>json.contribution_percent,
        twitterUsername: <string>json.twitter_username,
        nym: <string>json.nym,
        twitterProfileImageUrl: <string>json.twitter_profile_image_url,
        twitterUsernameVerified: <boolean>json.twitter_username_verified,
        twitterUsernameVerificationTweet: <string>json.twitter_username_verification_tweet,
        hasAuctions: <boolean>json.has_auctions,
        hasBids: <boolean>json.has_bids,
        isModerator: <boolean>json.is_moderator,
        runningAuctionCount: <number>json.running_auction_count,
        endedAuctionCount: <number>json.ended_auction_count
    }
}
