
export interface Bid {
    amount: number;
    twitter_username?: string;
    twitter_profile_image_url?: string;
    twitter_username_verified?: boolean;
    payment_request?: string;
}

export interface Media {
    url: string;
    twitter_media_key: string;
}

export interface Auction {
    key: string;
    title: string;
    description: string;
    starting_bid: number;
    reserve_bid: number;
    duration_hours: number;
    canceled: boolean;
    start_date?: Date | null;
    started?: boolean | null;
    end_date?: Date | null;
    ended?: boolean | null;
    duration_str?: string;
    bids: Bid[];
    media: Media[];

    invalidTitle?: boolean;
    invalidDescription?: boolean;
}

export function fromJson(json: Auction) {
    var a: Auction = {key: "", title: "", description: "", starting_bid: 0, reserve_bid: 0, duration_hours: 0, canceled: false, bids: [], media: []};
    for (var k in json) {
        if (k === 'start_date') {
            a.start_date = json[k] ? new Date(json[k]!) : null;
            a.started = a.start_date && a.start_date < new Date();
        } else if (k === 'end_date') {
            a.end_date = json[k] ? new Date(json[k]!) : null;
            a.ended = a.end_date && a.end_date < new Date();
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
            if (hours > 0) {
                durations.push(`${hours} hour${ hours > 1 ? "s" : ""}`);
            }
            a.duration_str = durations.join(" and ");
        } else {
            a[k] = json[k];
        }
    }
    return a;
}
