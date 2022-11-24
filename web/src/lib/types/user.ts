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

export interface Badge {
    badge: number;
    icon: string;
}

export function badgeFromJson(json: any): Badge {
    return {badge: <number>json.badge, icon: <string>json.icon};
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
    badges: Badge[] = [];

    public hasBadge(badge) {
        for (const b of this.badges) {
            if (b.badge === badge) {
                return true;
            }
        }

        return false;
    }

    public firstBadge(badge) {
        for (const b of this.badges) {
            if (b.badge === badge) {
                return b;
            }
        }

        return null;
    }
}

export function fromJson(json: any): User {
    var u = new User();
    u.nym = <string | null>json.nym;
    u.displayName = <string | null>json.display_name;
    u.profileImageUrl = <string | null>json.profile_image_url;
    u.email = <string | null>json.email;
    u.emailVerified = <boolean>json.email_verified;
    u.telegramUsername = <string | null>json.telegram_username;
    u.telegramUsernameVerified = <boolean>json.telegram_username_verified;
    u.twitterUsername = <string | null>json.twitter_username;
    u.twitterUsernameVerified = <boolean>json.twitter_username_verified;
    u.twitterVerificationPhraseSentAt = json.twitter_verification_phrase_sent_at ? new Date(json.twitter_verification_phrase_sent_at) : null;
    u.stallBannerUrl = <string | null>json.stall_banner_url;
    u.stallName = <string | null>json.stall_name;
    u.stallDescription = <string | null>json.stall_description;
    u.hasItems = <boolean>json.has_items;
    u.hasOwnItems = <boolean>json.has_own_items;
    u.hasActiveAuctions = <boolean>json.has_active_auctions;
    u.hasPastAuctions = <boolean>json.has_past_auctions;
    u.hasActiveListings = <boolean>json.has_active_listings;
    u.hasPastListings = <boolean>json.has_past_listings;
    u.contributionPercent = <number | null>json.contribution_percent;
    u.xpub = <string | null>json.xpub;
    u.isModerator = <boolean>json.is_moderator;
    u.badges = (json.badges as Array<any>).map(badgeFromJson);
    return u;
}
