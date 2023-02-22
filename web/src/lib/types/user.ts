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

export class UserResumeSkill {
    skill: string = "";

    public toJson() {
        return {skill: this.skill};
    }

    public static fromJson(json: any): UserResumeSkill {
        let s = new UserResumeSkill();
        s.skill = <string>json.skill;
        return s;
    }
}

export class UserResumePortfolio {
    url: string = "";

    public toJson() {
        return {url: this.url};
    }

    public static fromJson(json: any): UserResumePortfolio {
        let p = new UserResumePortfolio();
        p.url = <string>json.url;
        return p;
    }
}

export class UserResumeEducation {
    key: string = "";
    year: number | null = null;
    education: string = "";

    public validate() {
        return !(this.education.length === 0);
    }

    public toJson() {
        return {key: this.key, year: this.year, education: this.education};
    };

    public static fromJson(json: any): UserResumeEducation {
        let e = new UserResumeEducation();
        e.key = <string>json.key;
        e.education = <string>json.education;
        return e;
    }
}

export class UserResumeExperience {
    key: string = "";
    fromYear: number | null = null;
    fromMonth: number | null = null;
    toYear: number | null = null;
    toMonth: number | null = null;
    jobTitle: string = "";
    organization: string = "";
    description: string = "";

    public validate() {
        return !(this.jobTitle.length === 0) && !(this.organization.length === 0)
            && (this.fromMonth === null || (this.fromMonth > 0 && this.fromMonth <= 12))
            && (this.toMonth === null || (this.toMonth > 0 && this.toMonth <= 12));
    }

    public toJson() {
        return {
            key: this.key,
            from_year: this.fromYear, from_month: this.fromMonth,
            to_year: this.toYear, to_month: this.toMonth,
            job_title: this.jobTitle, organization: this.organization, description: this.description
        };
    };

    public static fromJson(json: any): UserResumeExperience {
        let e = new UserResumeExperience();
        e.key = <string>json.key;
        e.fromYear = <number | null>json.from_year;
        e.fromMonth = <number | null>json.from_month;
        e.toYear = <number | null>json.to_year;
        e.toMonth = <number | null>json.to_month;
        e.jobTitle = <string>json.job_title;
        e.organization = <string>json.organization;
        e.description = <string>json.description;
        return e;
    }
}

export class UserResumeAchievement {
    key: string = "";
    year: number | null = null;
    achievement: string = "";

    public validate() {
        return !(this.achievement.length === 0);
    }

    public toJson() {
        return {key: this.key, year: this.year, achievement: this.achievement};
    };

    public static fromJson(json: any): UserResumeAchievement {
        let a = new UserResumeAchievement();
        a.key = <string>json.key;
        a.year = <number | null>json.year;
        a.achievement = <string>json.achievement;
        return a;
    }
}

export class UserResume {
    jobTitle: string = "";
    bio: string = "";
    desiredSalaryUsd: number | null = null;
    bitcoinerQuestion: string = "";
    skills: UserResumeSkill[] = [];
    portfolio: UserResumePortfolio[] = [];
    education: UserResumeEducation[] = [];
    experience: UserResumeExperience[] = [];
    achievements: UserResumeAchievement[] = [];

    public toJson() {
        return {
            job_title: this.jobTitle,
            bio: this.bio,
            desired_salary_usd: this.desiredSalaryUsd,
            bitcoiner_question: this.bitcoinerQuestion,
            skills: this.skills.map(s => s.toJson()),
            portfolio: this.portfolio.map(p => p.toJson()),
            education: this.education.map(e => e.toJson()),
            experience: this.experience.map(e => e.toJson()),
            achievements: this.achievements.map(a => a.toJson()),
        };
    }

    public static fromJson(json: any): UserResume {
        let r = new UserResume();
        r.jobTitle = <string>json.job_title;
        r.bio = <string>json.bio;
        r.desiredSalaryUsd = <number | null>json.desired_salary_usd;
        r.bitcoinerQuestion = <string>json.bitcoiner_question;
        r.skills = (<any[]>json.skills).map(s => UserResumeSkill.fromJson(s));
        r.portfolio = (<any[]>json.portfolio).map(p => UserResumePortfolio.fromJson(p));
        r.education = (<any[]>json.education).map(e => UserResumeEducation.fromJson(e));
        r.experience = (<any[]>json.experience).map(e => UserResumeExperience.fromJson(e));
        r.achievements = (<any[]>json.achievements).map(a => UserResumeAchievement.fromJson(a));
        return r;
    }
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
    nostrPublicKey: string | null = null;
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

    // NB: this is the private key generated by PM.
    // if you use a browser extension such as Alby, we never have access to the private key!
    // TODO: probably we should rename this to something else (add "generated" prefix?) to avoid confusion with the nostrPublicKey we also store
    // also - we should make it camelCase, same as all other fields in this class
    nostr_private_key: string | null = null;

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
    u.nostrPublicKey = <string | null>json.nostr_public_key;
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

    return u;
}
