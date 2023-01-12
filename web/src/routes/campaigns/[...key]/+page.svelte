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
    import FaketoshiPNG from "$lib/images/Bitko-Illustration-Faketoshi.png?url"

    /** @type {import('./$types').PageData} */
    export let data;

    let campaign: Campaign;

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
        title={data.serverLoadedCampaign.getShortName()}
        description={data.serverLoadedCampaign.getShortDescription()}
        openGraph={{
            site_name: "Plebeian Market",
            type: "website",
            url: $page.url.href,
            title: data.serverLoadedCampaign.getShortName(),
            description: data.serverLoadedCampaign.getShortDescription(),
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
            imageAlt: data.serverLoadedCampaign.getShortName(),
        }}
/>
{/if}

{#if data.campaignKey === "" || data.campaignKey === null}
    {#if $user && $user.isModerator}
    <div class="grid place-items-center py-20 lg:w-2/3 mx-auto p-2">

      <h3 class="lg:text-8xl text-5xl font-bold">My campaigns</h3>
      <ListView
              loader={{endpoint: 'users/me/campaigns', responseField: 'campaigns', fromJson}}
              postEndpoint="users/me/campaigns"
              card={CampaignCard}
              editor={CampaignEditor}
              style={ListViewStyle.List}>
          <div slot="new-entity" class="flex justify-center" let:setCurrent={setCurrent}>
              <div class="mx-auto my-10 btn btn-primary" on:click|preventDefault={() => setCurrent(new Campaign())}>Create a new Campaign</div>
          </div>
      </ListView>
    </div>
    {:else}
        <div class="alert alert-info shadow-lg mt-8">
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
        campaignKey={campaign.key}
        showItemsOwner={true}
        showItemsCampaign={false}
        canAddItems={true}>
        <div slot="extra-description" class="">

                <div class="p-10 rounded mt-4 text-center">
                    Note: 100% of the money from the sales in this campaign will go to addresses generated from the following XPUB provided by Defending BTC team.
                    <div class="text-center">
                        <input value={campaign.xpub} type="text" class="input input-bordered w-full max-w-xs" disabled />
                        <button class="btn ml-2 mt-2 w-20" on:click={copyXpub}>{#if xpubCopied}Copied{:else}Copy!{/if}</button>
                        <p class="mt-8 text-4xl font-bold">Don't trust, verify!</p>
                    </div>
                </div>

        </div>
    </StallView>
{/if}
