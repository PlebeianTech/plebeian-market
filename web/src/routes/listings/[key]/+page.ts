import { getApiBaseUrl } from "$lib/utils";

export async function load({ params }) {
    const { key } = params;

    const listingUrl = `${getApiBaseUrl()}/api/listings/${key}`;
    const response = await fetch(listingUrl)
    const listing = await response.json()
    if (response.ok) {
        return {
            itemKey: key,
            serverLoadedItem: listing.listing
        }
    }
    return {
        status: response.status,
        error: new Error("Could not fetch listing on the server")
    }
}
