import type { IEntity } from "$lib/types/base";
import type { IAccount } from "$lib/types/user";

export class Campaign implements IEntity {
    endpoint = 'campaigns';

    key: string = "";
    title: string = "";
    description: string = "";

    started: boolean = false;
    ended: boolean = false;

    owner: IAccount = {nym: null, profileImageUrl: null, twitterUsername: null, twitterUsernameVerified: false};

    public validate() {
        return true;
    }

    public toJson() {
        return JSON.stringify(
            {
                title: this.title,
                description: this.description,
            });
    }
}

export function fromJson(json: any): Campaign {
    let campaign = new Campaign();
    campaign.key = <string>json.key;
    campaign.title = <string>json.title;
    campaign.description = <string>json.description;
    campaign.started = <boolean>json.started;
    campaign.ended = <boolean>json.ended;
    campaign.owner = {
        nym: <string>json.owner_nym,
        profileImageUrl: <string | null>json.owner_profile_image_url,
        twitterUsername: <string | null>json.owner_twitter_username,
        twitterUsernameVerified: <boolean>json.owner_twitter_username_verified,
    };

    return campaign;
}