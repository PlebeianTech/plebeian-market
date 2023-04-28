<script lang="ts">
    import { onMount } from 'svelte';
    import CampaignCard from "$lib/components/CampaignCard.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import StallView from "$lib/components/StallView.svelte";
    import { Campaign, fromJson } from "$lib/types/campaign";
    import { getItem, ErrorHandler } from "$lib/services/api";
    import { token, user } from "$lib/stores";
    import { MetaTags } from "svelte-meta-tags";
    import { page } from "$app/stores";
    import { getShortTitle, getShortDescription } from "$lib/utils";
    import FaketoshiPNG from "$lib/images/Bitko-Illustration-Faketoshi.png?url"

    /** @type {import('./$types').PageData} */
    export let data;

    let campaign: Campaign;

    let walletCopied = false;
    function copyWallet() {
        if (campaign.wallet !== null) {
            navigator.clipboard.writeText(campaign.wallet);
            walletCopied = true;
        }
    }

    let loading = false;
    function fetchCampaign(k: string) {
        loading = true;
        getItem({endpoint: 'campaigns', responseField: 'campaign', fromJson}, $token, k,
            c => {
                campaign = c;
                loading = false;
            },
            new ErrorHandler(false, () => {
                loading = false;
            }));
    }

    onMount(async () => {
        if (!(data.campaignKey === "" || data.campaignKey === null)) {
            fetchCampaign(data.campaignKey);
        }
    });
</script>

{#if data.serverLoadedCampaign}
    <MetaTags
            title={getShortTitle(data.serverLoadedCampaign.name)}
            description={getShortDescription(data.serverLoadedCampaign.description)}
            openGraph={{
                site_name: import.meta.env.VITE_SITE_NAME,
                type: "website",
                url: $page.url.href,
                title: getShortTitle(data.serverLoadedCampaign.name),
                description: getShortDescription(data.serverLoadedCampaign.description),
                images: [
                {
                    url: FaketoshiPNG,
                    alt: "Art by Bitko Yinowsky"
                }
                ],
            }}
            twitter={{
                site: import.meta.env.VITE_TWITTER_USER,
                handle: import.meta.env.VITE_TWITTER_USER,
                cardType: "summary_large_image",
                image: FaketoshiPNG,
                imageAlt: getShortTitle(data.serverLoadedCampaign.name),
            }}
    />
{/if}

{#if data.campaignKey === "" || data.campaignKey === null}
    <div class="grid place-items-center py-20 lg:w-2/3 mx-auto p-2">
        <h3 class="lg:text-8xl text-5xl font-bold">Campaigns</h3>
        <ListView
                loader={{endpoint: 'campaigns/active', responseField: 'campaigns', fromJson}}
                card={CampaignCard}
                editor={null}
                style={ListViewStyle.List}>
        </ListView>
    </div>
{:else if loading}
    <Loading />
{:else if campaign}
    <StallView
        baseUrl={`campaigns/${data.campaignKey}`}
        bannerUrl={campaign.banner_url}
        owner={campaign.owner}
        title={campaign.name}
        description={campaign.description}
        isCampaignStall={true}
        campaignKey={campaign.key}
        showItemsOwner={true}
        showItemsCampaign={false}
        canAddItems={true}>
        <div slot="extra-description" class="">
            <div class="p-10 rounded mt-4 text-center">
                Note: 100% of the money from the sales in this campaign will go to addresses generated from the following XPUB provided by Defending BTC team.
                <div class="text-center">
                    <input value={campaign.wallet} type="text" class="input input-bordered w-full max-w-xs" disabled />
                    <button class="btn ml-2 mt-2 w-20" on:click={copyWallet}>{#if walletCopied}Copied{:else}Copy!{/if}</button>
                    <p class="mt-8 text-4xl font-bold">Don't trust, verify!</p>
                </div>
            </div>
        </div>
    </StallView>
{/if}
