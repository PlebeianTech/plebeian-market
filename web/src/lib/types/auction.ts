import { isProduction } from "$lib/utils";
import type { IEntity } from "$lib/types/base";
import { Category, type Item, type Media, TIME_ITEM_DESCRIPTION_PLACEHOLDER } from "$lib/types/item";
import { type Sale, fromJson as saleFromJson } from "$lib/types/sale";
import type { IAccount } from "$lib/types/user";

export interface Bid {
    amount: number;
    buyer: IAccount;
    payment_request?: string;
    settled_at?: Date;
    is_winning_bid: boolean;
}

export interface BidThreshold {
    bid_amount_usd: number;
    required_badge: number;
}

export function bidThresholdFromJson(json: any): BidThreshold {
    return {bid_amount_usd: <number>json.bid_amount_usd, required_badge: <number>json.required_badge};
}

export class Auction implements IEntity, Item {
    static SAVED_FIELDS = ['title', 'description', 'category', 'shipping_from', 'shipping_domestic_usd', 'shipping_worldwide_usd', 'starting_bid', 'reserve_bid', 'duration_hours'];

    endpoint = "auctions";
    loader = {endpoint: this.endpoint, responseField: 'auction', fromJson};

    key: string = "";
    title: string = "";
    seller: IAccount = {nym: null, displayName: null, profileImageUrl: null, email: null, emailVerified: false, telegramUsername: null, telegramUsernameVerified: false, twitterUsername: null, twitterUsernameVerified: false};
    description: string = "";
    descriptionPlaceholder: string = "";
    category: string | null = null;
    starting_bid: number = 0;
    reserve_bid: number = 0;
    reserve_bid_reached: boolean = false;
    shipping_from: string = "";
    shipping_domestic_usd: number = 0;
    shipping_worldwide_usd: number = 0;
    duration_hours: number = isProduction() ? 3 * 24 : 24;
    start_date?: Date | null;
    started: boolean = false;
    end_date?: Date | null;
    end_date_extended: boolean = false;
    ended: boolean = false;
    duration_str?: string;
    bids: Bid[] = [];
    sales: Sale[] = [];
    media: Media[] = [];
    campaign_key: string | null = null;
    campaign_name: string | null = null;
    bid_thresholds: BidThreshold[] = [];
    is_mine: boolean = true;
    following: boolean = false;
    has_winner?: boolean = false;
    winner? : IAccount;

    public validate() {
        return !(this.title.length === 0 || this.description.length === 0);
    }

    public topBid() {
        var top: Bid | undefined = undefined;
        for (const bid of this.bids) {
            if (top === undefined || bid.amount > top.amount) {
                top = bid;
            }
        }
        return top;
    }

    public topAmount() {
        var top = this.topBid();
        return top === undefined ? 0 : top.amount;
    }

    public nextBid() {
        var lastBid = this.topAmount() || this.starting_bid;
        var head = String(lastBid).slice(0, 2);
        var rest = String(lastBid).slice(2);
    
        if (head[0] === "1") {
            head = String(Number(head) + 1);
        } else if (head[0] === "2") {
            head = String(Number(head) + 2);
        } else if (head[0] === "3" || head[0] === "4") {
            if (head[1] === "0") {
                head = head[0] + "2";
            } else if (head[1] === "1" || head[1] === "2" || head[1] === "3") {
                head = head[0] + "5";
            } else if (head[1] === "4" || head[1] === "5" || head[1] === "6" ||  head[1] === "7") {
                head = head[0] + "8";
            } else {
                head = String(Number(head[0]) + 1) + "0";
            }
        } else {
            if (head[1] === "0" || head[1] === "1" || head[1] === "2" || head[1] === "3") {
                head = head[0] + "5";
            } else {
                head = String(Number(head[0]) + 1) + "0";
            }
        }
    
        return Number(head + rest);
    }

    public toJson() {
        var json = {} as Record<string, any>;
        for (const k in this) {
            if (Auction.SAVED_FIELDS.indexOf(k) !== -1 && this[k] !== null) {
                json[k] = this[k];
            }
        }
        return JSON.stringify(json);
    }
}

export class TimeAuction extends Auction {
    constructor() {
        super();
        this.category = Category.Time;
        this.descriptionPlaceholder = TIME_ITEM_DESCRIPTION_PLACEHOLDER;
    }
}

export function fromJson(json: any): IEntity {
    var a = new Auction();
    for (var k in json) {
        if (k === 'start_date') {
            a.start_date = json[k] ? new Date(json[k]!) : null;
        } else if (k === 'end_date') {
            a.end_date = json[k] ? new Date(json[k]!) : null;
        } else if (k === 'duration_hours') {
            a.duration_hours = json[k] || 0;
            let days = 0, hours = a.duration_hours!;
            if (hours >= 24) {
                days = Math.floor(hours / 24);
                hours = hours % 24;
            }
            let durations: string[] = [];
            if (days > 0) {
                durations.push(`${days} day${ days > 1 ? "s" : ""}`);
            }
            if (hours >= 1) {
                durations.push(`${hours} hour${ hours > 1 ? "s" : ""}`);
            } else if (hours > 0) {
                durations.push(`${60 * hours} min`);
            }
            a.duration_str = durations.join(" and ");
        } else if (k === 'bids') {
            for (const bidjson of json[k]) {
                var b: Bid = {amount: 0, buyer: {nym: null, displayName: null, profileImageUrl: null, email: null, emailVerified: false, telegramUsername: null, telegramUsernameVerified: false, twitterUsername: null, twitterUsernameVerified: false}, is_winning_bid: false};
                for (var kk in bidjson) {
                    if (kk === 'settled_at') {
                        b.settled_at = new Date(bidjson[kk]);
                    } else {
                        b[kk] = bidjson[kk];
                    }
                }
                b.buyer = {
                    nym: <string>bidjson.buyer_nym,
                    displayName: <string>bidjson.buyer_display_name,
                    profileImageUrl: <string | null>bidjson.buyer_profile_image_url,
                    email: <string | null>bidjson.buyer_email,
                    emailVerified: <boolean>bidjson.buyer_email_verified,
                    telegramUsername: <string | null>bidjson.buyer_telegram_username,
                    telegramUsernameVerified: <boolean>bidjson.buyer_telegram_username_verified,
                    twitterUsername: <string | null>bidjson.buyer_twitter_username,
                    twitterUsernameVerified: <boolean>bidjson.buyer_twitter_username_verified,
                };
                a.bids.push(b);
            }
        } else if (k === 'bid_thresholds') {
            a.bid_thresholds = (json[k] as Array<any>).map(bidThresholdFromJson);
        } else if (k === 'sales') {
            a.sales = (json[k] as Array<any>).map(saleFromJson);
        } else {
            a[k] = json[k];
        }
    }
    a.seller = {
        nym: <string>json.seller_nym,
        displayName: <string>json.seller_display_name,
        profileImageUrl: <string | null>json.seller_profile_image_url,
        email: <string | null>json.seller_email,
        emailVerified: <boolean>json.seller_email_verified,
        telegramUsername: <string | null>json.seller_telegram_username,
        telegramUsernameVerified: <boolean>json.seller_telegram_username_verified,
        twitterUsername: <string | null>json.seller_twitter_username,
        twitterUsernameVerified: <boolean>json.seller_twitter_username_verified,
    };
    if (json.winner_nym) {
        a.winner = {
            nym: <string>json.winner_nym,
            displayName: <string>json.winner_display_name,
            profileImageUrl: <string | null>json.winner_profile_image_url,
            email: <string | null>json.winner_email,
            emailVerified: <boolean>json.winner_email_verified,
            telegramUsername: <string | null>json.winner_telegram_username,
            telegramUsernameVerified: <boolean>json.winner_telegram_username_verified,
            twitterUsername: <string | null>json.winner_twitter_username,
            twitterUsernameVerified: <boolean>json.winner_twitter_username_verified,
        };
    }
    return a;
}
