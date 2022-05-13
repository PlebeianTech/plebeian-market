
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

export interface Auction {
    key: string;
    title: string;
    description: string;
    starting_bid: number;
    reserve_bid: number;
    duration_hours: number;
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

export function fromJson(json: any) {
    var a: Auction = {key: "", title: "", description: "", starting_bid: 0, reserve_bid: 0, duration_hours: 0, bids: [], media: []};
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

export function nextBid(lastBid) {
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
