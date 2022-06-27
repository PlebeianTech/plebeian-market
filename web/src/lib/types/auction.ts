import { isLocal, isStaging } from "../utils";

export interface Bid {
    amount: number;
    twitter_username?: string;
    twitter_profile_image_url?: string;
    twitter_username_verified?: boolean;
    payment_request?: string;
    settled_at?: Date;
}

export interface Media {
    url: string;
    twitter_media_key: string;
}

export class Auction {
    static SAVED_FIELDS = ['title', 'description', 'shipping_from', 'starting_bid', 'reserve_bid', 'duration_hours'];

    key: string = "";
    title: string = "";
    seller_twitter_username: string = "";
    seller_twitter_username_verified: boolean = false;
    seller_twitter_profile_image_url: string = "";
    description: string = "";
    starting_bid: number = 0;
    reserve_bid: number = 0;
    reserve_bid_reached: boolean = false;
    shipping_from: string = "";
    duration_hours: number = isLocal() || isStaging() ? 24 : 3 * 24;
    start_date?: Date | null;
    started: boolean = false;
    end_date?: Date | null;
    end_date_extended: boolean = false;
    ended: boolean = false;
    duration_str?: string;
    bids: Bid[] = [];
    media: Media[] = [];
    is_mine: boolean = true;

    contribution_percent?: number;
    contribution_amount?: number;
    contribution_payment_request?: string;
    contribution_qr?: string;
    remaining_amount?: number;

    needs_contribution?: boolean;
    wait_contribution?: boolean;
    has_winner?: boolean;
    is_won?: boolean;

    is_lost?: boolean;
    winner_twitter_username?: string;
    winner_twitter_username_verified?: boolean;
    winner_twitter_profile_image_url?: string;

    invalidTitle?: boolean;
    invalidDescription?: boolean;

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
            if (Auction.SAVED_FIELDS.indexOf(k) !== -1) {
                json[k] = this[k];
            }
        }
        return JSON.stringify(json);
    }
}

export function fromJson(json: any) {
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
                var b: Bid = {amount: 0};
                for (var kk in bidjson) {
                    if (kk === 'settled_at') {
                        b.settled_at = new Date(bidjson[kk]);
                    } else {
                        b[kk] = bidjson[kk];
                    }
                }
                a.bids.push(b);
            }
        } else {
            a[k] = json[k];
        }
    }
    return a;
}

