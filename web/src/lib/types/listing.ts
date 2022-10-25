import type { IEntity } from "$lib/types/base";
import { type Item, Category, type Media } from "$lib/types/item";
import { type Sale, fromJson as saleFromJson } from "$lib/types/sale";
import type { IAccount } from "$lib/types/user";

export class Listing implements IEntity, Item {
    static SAVED_FIELDS = ['title', 'description', 'category', 'shipping_from', 'shipping_domestic_usd', 'shipping_worldwide_usd', 'price_usd', 'available_quantity'];

    endpoint = "listings";
    loader = {endpoint: this.endpoint, responseField: 'listing', fromJson};

    key: string = "";
    title: string = "";
    seller: IAccount = {nym: null, profileImageUrl: null, twitterUsername: null, twitterUsernameVerified: false};
    description: string = "";
    category: string | null = null;
    shipping_from: string = "";
    shipping_domestic_usd: number = 0;
    shipping_worldwide_usd: number = 0;
    price_usd: number = 0;
    available_quantity: number = 0;
    start_date?: Date | null;
    started: boolean = false;
    ended: boolean = false;
    sales: Sale[] = [];
    media: Media[] = [];
    campaign_key: string | null = null;
    campaign_name: string | null = null;
    is_mine: boolean = true;

    public validate() {
        return !(this.title.length === 0
            || this.description.length === 0
            || this.price_usd === null || this.price_usd === 0
            || this.available_quantity === null || this.available_quantity === 0);
    }

    public toJson() {
        var json = {} as Record<string, any>;
        for (const k in this) {
            if (Listing.SAVED_FIELDS.indexOf(k) !== -1 && this[k] !== null) {
                json[k] = this[k];
            }
        }
        return JSON.stringify(json);
    }
}

export class TimeListing extends Listing {
    constructor(nym: string) {
        super();
        this.category = Category.Time;
        this.title = `1 hour one-to-one call with ${nym}`;
    }
}

export function fromJson(json: any): IEntity {
    var l = new Listing();
    for (var k in json) {
        if (k === 'start_date') {
            l.start_date = json[k] ? new Date(json[k]!) : null;
        } else if (k === 'sales') {
            l.sales = (json[k] as Array<any>).map(saleFromJson);
        } else {
            l[k] = json[k];
        }
    }
    l.seller = {
        nym: <string>json.seller_nym,
        profileImageUrl: <string | null>json.seller_profile_image_url,
        twitterUsername: <string | null>json.seller_twitter_username,
        twitterUsernameVerified: <boolean>json.seller_twitter_username_verified,
    };
    return l;
}
