import type { IEntity } from "$lib/types/base";
import type { IAccount } from "$lib/types/user";

export class Campaign implements IEntity {
    static SAVED_FIELDS = ['name', 'description', 'wallet'];

    endpoint = 'campaigns';

    key: string = "";
    banner_url: string | null = null;
    name: string = "";
    description: string = "";
    is_mine: boolean = true;
    wallet: string | null = null;
    owner: IAccount = {nym: null, displayName: null, profileImageUrl: null, email: null, emailVerified: false, telegramUsername: null, telegramUsernameVerified: false, twitterUsername: null, twitterUsernameVerified: false, nostrPublicKey: null, nostrPublicKeyVerified: false};

    public validate() {
        return true;
    }

    public toJson() {
        var json = {} as Record<string, any>;
        for (const k in this) {
            if (Campaign.SAVED_FIELDS.indexOf(k) !== -1 && this[k] !== null) {
                json[k] = this[k];
            }
        }
        return JSON.stringify(json);
    }
}

export function fromJson(json: any): Campaign {
    let campaign = new Campaign();
    campaign.key = <string>json.key;
    campaign.banner_url = <string | null>json.banner_url;
    campaign.name = <string>json.name;
    campaign.description = <string>json.description;
    campaign.is_mine = <boolean>json.is_mine;
    campaign.wallet = <string | null>json.wallet;
    campaign.owner = {
        nym: <string>json.owner_nym,
        displayName: <string>json.owner_display_name,
        profileImageUrl: <string | null>json.owner_profile_image_url,
        email: <string | null>json.owner_email,
        emailVerified: <boolean>json.owner_email_verified,
        telegramUsername: <string | null>json.owner_telegram_username,
        telegramUsernameVerified: <boolean>json.owner_telegram_username_verified,
        twitterUsername: <string | null>json.owner_twitter_username,
        twitterUsernameVerified: <boolean>json.owner_twitter_username_verified,
        nostrPublicKey: null,
        nostrPublicKeyVerified: false,
    };

    return campaign;
}
