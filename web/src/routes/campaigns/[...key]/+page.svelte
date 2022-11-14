<script lang="ts">
    import { onMount } from 'svelte';
    import CampaignCard from "$lib/components/CampaignCard.svelte";
    import CampaignEditor from "$lib/components/CampaignEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import StallView from "$lib/components/StallView.svelte";
    import { Campaign, fromJson } from "$lib/types/campaign";
    import { getItem, ErrorHandler } from "$lib/services/api";
    import { token, user } from "$lib/stores";
    import { MetaTags } from "svelte-meta-tags";
    import { page } from "$app/stores";

    /** @type {import('./$types').PageData} */
    export let data;

    let campaign: Campaign;

    let showXpub = false;
    let xpubCopied = false;
    function copyXpub() {
        navigator.clipboard.writeText(campaign.xpub!);
        xpubCopied = true;
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
        title={data.serverLoadedCampaign.name ?? "Check this Plebeian Market Campaign!"}
        description={data.serverLoadedCampaign.description ?? "Check the products being sold and auctioned at this Plebeian Market Campaign!"}
        openGraph={{
            site_name: "Plebeian Market",
            type: "website",
            url: $page.url.href,
            title: data.serverLoadedCampaign.name ?? "Check this Plebeian Market Campaign!",
            description: data.serverLoadedCampaign.description ?? "Check the products being sold and auctioned at this Plebeian Market Campaign!",
            images: [
              {
                url: data.serverLoadedCampaign.banner_url ?? data.serverLoadedCampaign.owner_profile_image_url ?? "",
                alt: "My Stall picture"
              }
            ],
        }}
        twitter={{
            site: import.meta.env.VITE_TWITTER_USER,
            handle: import.meta.env.VITE_TWITTER_USER,
            cardType: "summary_large_image",
            image: data.serverLoadedCampaign.banner_url ?? data.serverLoadedCampaign.owner_profile_image_url ?? "",
            imageAlt: data.serverLoadedCampaign.name ?? "Check this Plebeian Market Campaign!",
        }}
/>
{/if}

{#if data.campaignKey === "" || data.campaignKey === null}
    {#if $user && $user.isModerator}
        <h3 class="text-xl">My campaigns</h3>
        <ListView
                loader={{endpoint: 'users/me/campaigns', responseField: 'campaigns', fromJson}}
                postEndpoint="users/me/campaigns"
                card={CampaignCard}
                editor={CampaignEditor}
                style={ListViewStyle.List}>
            <div slot="new-entity" let:setCurrent={setCurrent}>
                <div class="mx-auto my-10 glowbutton glowbutton-new" on:click|preventDefault={() => setCurrent(new Campaign())}></div>
            </div>
        </ListView>
    {:else}
        <div class="alert alert-info shadow-lg">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span>Please contact us if you want to launch a campaign!</span>
            </div>
        </div>
    {/if}
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
        showItemsOwner={true}
        showItemsCampaign={false}
        canAddItems={true}>
        <div slot="extra-description" class="mt-4">
            {#if showXpub}
                <div class="bg-base-300 p-10 rounded mt-6">
                    Note: all money from the sales in this campaign will go to addresses generated from the following XPUB.
                    <div class="text-center">
                        <input value={campaign.xpub} type="text" class="input input-bordered w-full max-w-xs" disabled />
                        <button class="btn ml-2 mt-2 w-20" on:click={copyXpub}>{#if xpubCopied}Copied{:else}Copy!{/if}</button>
                        <span class="ml-2">Don't trust, verify!</span>
                    </div>
                </div>
            {:else}
                <div class="flex flex-row-reverse">
                    <button class="btn btn-sm" on:click={() => showXpub = true}>Show XPUB</button>
                </div>
            {/if}
        </div>
    </StallView>
{/if}
