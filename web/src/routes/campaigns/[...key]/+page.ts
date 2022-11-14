import { getApiBaseUrl } from "$lib/utils";

export async function load({ params }) {
    const { key } = params;

    const campaignUrl = `${getApiBaseUrl()}api/campaigns/${key}`;
    const response = await fetch(campaignUrl)
    const campaign = await response.json()
    if (response.ok) {
        return {
            campaignKey: key,
            serverLoadedCampaign: campaign.campaign
        }
    }
    return {
        status: response.status,
        error: new Error("Could not fetch auction on the server")
    }
}
