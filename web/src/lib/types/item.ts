import type { ILoader } from "$lib/services/api";
import type { IAccount } from "$lib/types/user";

export interface Media {
    url: string;
    twitter_media_key: string;
}

export interface Item {
    endpoint: string;
    loader: ILoader;
    key: string;
    seller: IAccount;
    title: string;
    description: string;
    start_date?: Date | null;
    started: boolean;
    end_date?: Date | null;
    ended: boolean;
    shipping_from: string;
    shipping_estimate_domestic: string;
    shipping_estimate_worldwide: string;
    media: Media[];
    is_mine: boolean;
}