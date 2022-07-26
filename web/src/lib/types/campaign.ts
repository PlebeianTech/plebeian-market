import type { IEntity } from "$lib/types/base";
import type { IAccount } from "$lib/types/user";

export class Campaign implements IEntity {
    endpoint = 'campaigns';

    key: string = "";
    title: string = "";
    description: string = "";

    started: boolean = false;
    ended: boolean = false;

    owner: IAccount = {username: "", usernameVerified: false, profileImageUrl: ""};

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
            username: <string>json.owner_twitter_username,
            usernameVerified: <boolean>json.owner_twitter_username_verified,
            profileImageUrl: <string>json.owner_twitter_profile_image_url
    };

    return campaign;
}