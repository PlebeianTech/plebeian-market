
export interface User {
    contributionPercent: number;
    twitterUsername: string;
    twitterUsernameVerified: boolean;
    hasAuctions: boolean;
    hasBids: boolean;
}

export function fromJson(json: any) {
    return {
        contributionPercent: <number>json.contribution_percent,
        twitterUsername: <string>json.twitter_username,
        twitterUsernameVerified: <boolean>json.twitter_username_verified,
        hasAuctions: <boolean>json.has_auctions,
        hasBids: <boolean>json.has_bids
    }
}
