import type { IEntity } from "$lib/types/base";

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

export class UserAchievement implements IEntity {
    static SAVED_FIELDS = ['achievement', 'from_year', 'from_month', 'to_year', 'to_month'];

    is_mine = true;
    endpoint: string = "users/me/achievements";
    key: string = "";
    achievement: string = "";
    from_year: number | null = null;
    from_month: number | null = null;
    to_year: number | null = null;
    to_month: number | null = null;

    public validate() {
        return !(this.achievement.length === 0)
            && (this.from_month === null || (this.from_month > 0 && this.from_month <= 12))
            && (this.to_month === null || (this.to_month > 0 && this.to_month <= 12));
    }

    public toJson() {
        var json = {} as Record<string, any>;
        for (const k in this) {
            if (UserAchievement.SAVED_FIELDS.indexOf(k) !== -1) {
                json[k] = this[k];
            }
        }
        return JSON.stringify(json);
    };
}

export interface Badge {
    badge: number;
    icon: string;
}

export function badgeFromJson(json: any): Badge {
    return {badge: <number>json.badge, icon: <string>json.icon};
}

export class User implements IAccount {
    identity: string = '';
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
    nostr_private_key: string | null = null;
    jobTitle: string | null = null;
    bio: string | null = null;
    desiredSalaryUsd: number | null = null;
    bitcoinerQuestion: string | null = null;
    skills: string[] = [];

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
    u.identity = <string>json.identity;
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
    u.nostr_private_key = <string | null>json.nostr_private_key;
    u.jobTitle = <string | null>json.job_title;
    u.bio = <string | null>json.bio;
    u.desiredSalaryUsd = <number | null>json.desired_salary_usd;
    u.bitcoinerQuestion = <string | null>json.bitcoiner_question;
    u.skills = <string[]>json.skills;

    return u;
}

export function userAchievementFromJson(json: any): UserAchievement {
    let achievement = new UserAchievement();
    achievement.key = <string>json.key;
    achievement.achievement = <string>json.achievement;
    achievement.from_year = <number | null>json.from_year;
    achievement.from_month = <number | null>json.from_month;
    achievement.to_year = <number | null>json.to_year;
    achievement.to_month = <number | null>json.to_month;
    return achievement;
}
