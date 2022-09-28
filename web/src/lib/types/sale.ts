import type { IEntity } from "$lib/types/base";
import type { IAccount } from "$lib/types/user";

export enum SaleState {
    REQUESTED = 'REQUESTED',
    CONTRIBUTION_SETTLED = 'CONTRIBUTION_SETTLED',
    TX_DETECTED = 'TX_DETECTED',
    TX_CONFIRMED = 'TX_CONFIRMED',
    EXPIRED = 'EXPIRED',
}

export class Sale implements IEntity {
    key: string = "";
    endpoint = "sales";

    item_title: string = "";
    state: SaleState = SaleState.REQUESTED;
    price_usd: number = 0;
    price: number = 0;
    quantity: number = 0;
    amount: number = 0;
    shipping_domestic: number = 0;
    shipping_worldwide: number = 0;
    seller: IAccount = {nym: null, profileImageUrl: null, twitterUsername: null, twitterUsernameVerified: false};
    buyer: IAccount = {nym: null, profileImageUrl: null, twitterUsername: null, twitterUsernameVerified: false};
    contribution_amount: number = 0;
    contribution_payment_request: string = "";
    contribution_payment_qr: string | null = null;
    contribution_settled_at: Date | null = null;
    address: string = "";
    address_qr: string | null = null;
    txid: string = "";
    tx_value?: number = undefined;
    requested_at?: Date = undefined;
    settled_at?: Date = undefined;
    expired_at?: Date = undefined;

    public validate() {
        return false; // since we cannot create sales from the UI
    }

    public toJson() {
        return null; // since sales are read-only
    }

    public stateStr() {
        return this.state.toString().split("_").join(" ");
    }
}

export function fromJson(json: any): Sale {
    var s: Sale = new Sale();

    for (var k in json) {
        if (k === 'requested_at' || k === 'contribution_settled_at' || k === 'settled_at' || k === 'expired_at') {
            s[k] = new Date(json[k]);
        } else {
            s[k] = json[k];
        }
    }
    s.seller = {
        nym: <string>json.seller_nym,
        profileImageUrl: <string | null>json.seller_profile_image_url,
        twitterUsername: <string | null>json.seller_twitter_username,
        twitterUsernameVerified: <boolean>json.seller_twitter_username_verified,
    };
    s.buyer = {
        nym: <string>json.buyer_nym,
        profileImageUrl: <string | null>json.buyer_profile_image_url,
        twitterUsername: <string | null>json.buyer_twitter_username,
        twitterUsernameVerified: <boolean>json.buyer_twitter_username_verified,
    };

    return s;
}