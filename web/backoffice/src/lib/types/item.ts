import type { ILoader } from "$lib/services/api";
import type { Sale } from "$lib/types/sale";
import type { IAccount } from "$lib/types/user";

export interface Media {
    url: string;
}

// NB: we need to differentiate between Media that existed on an item (which has an URL pointing to the resource)
// and AddedMedia that is about to get added to an item - which is a file selected from the browser.
// To keep compatibility between the two, so for example the "Gallery" view works for both, the AddedMedia also has a "url",
// however this is the *actual content* of the file, which we read using a FileReader.
// The good part about this trick is that this "url" can be used in a <img src="..." />.
export interface AddedMedia extends Media {
    url: string;
    file: any;
}

export enum Category {
    Time = 'TIME',
}

export const TIME_ITEM_DESCRIPTION_PLACEHOLDER = "Please describe what the winner can expect. Can they ask anything or are there topics to avoid? Are $DOGE price predictions not your thing? What's your format? Jitsi, Keet, Zoom?";

export interface Item {
    endpoint: string;
    loader: ILoader;
    key: string;
    seller: IAccount;
    title: string;
    description: string;
    descriptionPlaceholder: string;
    category: string | null;
    start_date: Date | null;
    started: boolean;
    end_date?: Date | null;
    ended: boolean;
    shipping_from: string;
    shipping_domestic_usd: number;
    shipping_worldwide_usd: number;
    sales: Sale[];
    media: Media[];
    added_media: AddedMedia[];
    campaign_key: string | null;
    campaign_name: string | null;
    is_mine: boolean;
}
