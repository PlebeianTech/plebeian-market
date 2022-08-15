import type { IEntity } from "$lib/types/base";
import type { Item, Media } from "$lib/types/item";
import type { IAccount } from "$lib/types/user";

export interface Sale {
    price: number;
    quantity: number;
    buyer: IAccount;
    contribution_payment_request: string;
    contribution_settled_at: Date | null;
    address: string;
    settled_at: Date | null;
}

export class Listing implements IEntity, Item {
    static SAVED_FIELDS = ['title', 'description', 'shipping_from', 'shipping_estimate_domestic', 'shipping_estimate_worldwide', 'price_usd', 'available_quantity'];

    endpoint = "listings";
    loader = {endpoint: this.endpoint, responseField: 'listing', fromJson};

    key: string = "";
    title: string = "";
    seller: IAccount = {username: "", usernameVerified: false, profileImageUrl: ""};
    description: string = "";
    shipping_from: string = "";
    shipping_estimate_domestic: string = "";
    shipping_estimate_worldwide: string = "";
    price_usd: number = 0;
    available_quantity: number = 0;
    start_date?: Date | null;
    started: boolean = false;
    ended: boolean = false;
    sales: Sale[] = [];
    media: Media[] = [];
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
            if (Listing.SAVED_FIELDS.indexOf(k) !== -1) {
                json[k] = this[k];
            }
        }
        return JSON.stringify(json);
    }
}

export function fromJson(json: any): IEntity {
    var l = new Listing();
    for (var k in json) {
        if (k === 'start_date') {
            l.start_date = json[k] ? new Date(json[k]!) : null;
        } else if (k === 'sales') {
            for (const salejson of json[k]) {
                var s: Sale = {
                    price: 0, quantity: 0,
                    buyer: {username: "", profileImageUrl: "", usernameVerified: false},
                    address: "",
                    contribution_payment_request: "",
                    contribution_settled_at: null,
                    settled_at: null,
                };
                for (var kk in salejson) {
                    if (kk === 'settled_at') {
                        s.settled_at = salejson[kk] ? new Date(salejson[kk]) : null;
                    } else if (kk === 'contribution_settled_at') {
                        s.contribution_settled_at = salejson[kk] ? new Date(salejson[kk]) : null;
                    } else {
                        s[kk] = salejson[kk];
                    }
                }
                s.buyer = {
                    username: <string>salejson.twitter_username,
                    profileImageUrl: <string>salejson.twitter_profile_image_url,
                    usernameVerified: <boolean>salejson.twitter_username_verified,
                };
                l.sales.push(s);
            }
        } else {
            l[k] = json[k];
        }
    }
    l.seller = {
        username: <string>json.seller_twitter_username,
        usernameVerified: <boolean>json.seller_twitter_username_verified,
        profileImageUrl: <string>json.seller_twitter_profile_image_url
    };
    return l;
}
