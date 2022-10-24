import type { ILoader } from "$lib/services/api";
import type { Sale } from "$lib/types/sale";
import type { IAccount } from "$lib/types/user";

export interface Media {
    index: number;
    hash: string;
    url: string;
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
    shipping_domestic_usd: number;
    shipping_worldwide_usd: number;
    sales: Sale[];
    media: Media[];
    campaign_key: string | null;
    campaign_name: string | null;
    is_mine: boolean;
}