import { getApiBaseUrl } from "$lib/utils";

export async function load({ params }) {
    const { key } = params;

    const auctionUrl = `${getApiBaseUrl()}api/auctions/${key}`;
    const response = await fetch(auctionUrl)
    const auction = await response.json()
    if (response.ok) {
        return {
            itemKey: key,
            serverLoadedItem: auction.auction
        }
    }
    return {
        status: response.status,
        error: new Error("Could not fetch auction on the server")
    }
}
