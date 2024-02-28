import type { ILoader } from "$lib/services/api";

export interface Media {
    index: number;
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


export interface Item {
    endpoint: string;
    loader: ILoader;
    uuid: string;
    key: string;
    title: string;
    description: string;
    categories: string[];
    start_date: Date | null;
    started: boolean;
    end_date?: Date | null;
    ended: boolean;
    shipping_from: string;
    extra_shipping_domestic_usd: number;
    extra_shipping_worldwide_usd: number;
    media: Media[];
    added_media: AddedMedia[];
    is_mine: boolean;

    isPublished: () => boolean;
}
