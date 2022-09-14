import type { IEntity } from "$lib/types/base";
import type { Item, Media } from "$lib/types/item";
import type { IAccount } from "$lib/types/user";

export enum SaleState {
    REQUESTED = 'REQUESTED',
    CONTRIBUTION_SETTLED = 'CONTRIBUTION_SETTLED',
    TX_DETECTED = 'TX_DETECTED',
    TX_CONFIRMED = 'TX_CONFIRMED',
    EXPIRED = 'EXPIRED',
}

export interface Sale {
    state: SaleState;
    price: number;
    quantity: number;
    amount: number;
    shipping_domestic: number;
    shipping_worldwide: number;
    seller: IAccount;
    buyer: IAccount;
    contribution_amount: number;
    contribution_payment_request: string;
    contribution_payment_qr: string | null;
    contribution_settled_at: Date | null;
    address: string;
    address_qr: string | null;
    txid: string;
    settled_at: Date | null;
    expired_at: Date | null;
}

export class Listing implements IEntity, Item {
    static SAVED_FIELDS = ['title', 'description', 'shipping_from', 'shipping_domestic_usd', 'shipping_worldwide_usd', 'price_usd', 'available_quantity'];

    endpoint = "listings";
    loader = {endpoint: this.endpoint, responseField: 'listing', fromJson};

    key: string = "";
    title: string = "";
    seller: IAccount = {username: "", usernameVerified: false, profileImageUrl: ""};
    description: string = "";
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

export function saleFromJson(json: any): Sale {
    var s: Sale = {
        state: SaleState.REQUESTED,
        price: 0,
        quantity: 0,
        amount: 0,
        shipping_domestic: 0,
        shipping_worldwide: 0,
        seller: {username: "", profileImageUrl: "", usernameVerified: false},
        buyer: {username: "", profileImageUrl: "", usernameVerified: false},
        address: "",
        address_qr: null,
        contribution_amount: 0,
        contribution_payment_request: "",
        contribution_payment_qr: null,
        contribution_settled_at: null,
        txid: "",
        settled_at: null, expired_at: null,
    };
    for (var k in json) {
        if (k === 'contribution_settled_at' || k === 'settled_at' || k === 'expired_at') {
            s[k] = json[k] ? new Date(json[k]) : null;
        } else {
            s[k] = json[k];
        }
    }
    s.seller = {
        username: <string>json.seller_twitter_username,
        profileImageUrl: <string>json.seller_twitter_profile_image_url,
        usernameVerified: <boolean>json.seller_twitter_username_verified,
    };
    s.buyer = {
        username: <string>json.buyer_twitter_username,
        profileImageUrl: <string>json.buyer_twitter_profile_image_url,
        usernameVerified: <boolean>json.buyer_twitter_username_verified,
    };

    return s;
}

export function fromJson(json: any): IEntity {
    var l = new Listing();
    for (var k in json) {
        if (k === 'start_date') {
            l.start_date = json[k] ? new Date(json[k]!) : null;
        } else if (k === 'sales') {
            for (const salejson of json[k]) {
                l.sales.push(saleFromJson(salejson));
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
