<script context="module">
    export async function load({ params }) {
        const { key } = params;
        return { props: { campaignKey: key } }
    }
</script>

<script lang="ts">
    import { onMount } from 'svelte';
    import CampaignCard from "$lib/components/CampaignCard.svelte";
    import CampaignEditor from "$lib/components/CampaignEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import StallView from "$lib/components/StallView.svelte";
    import { Campaign, fromJson } from "$lib/types/campaign";
    import { getItem, putEntity, ErrorHandler } from "$lib/services/api";
    import { token } from "$lib/stores";

    export let campaignKey;
    let campaign: Campaign;

    let editing = false;

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

    function saveCampaign() {
        if (!campaign || !campaign.validate()) {
            return;
        }

        putEntity($token, campaign,
            () => {
                editing = false;
                fetchCampaign(campaign.key);
            });
    }

    onMount(async () => {
        if (!(campaignKey === "" || campaignKey === null)) {
            fetchCampaign(campaignKey);
        }
    });
</script>

{#if campaignKey === "" || campaignKey === null}
    <h3 class="text-xl">My campaigns</h3>
    <ListView
        loader={{endpoint: 'users/me/campaigns', responseField: 'campaigns', fromJson}}
        postEndpoint="users/me/campaigns"
        newEntity={() => new Campaign()}
        card={CampaignCard} editor={CampaignEditor}
        style={ListViewStyle.List} />
{:else if loading}
    <Loading />
{:else if campaign}
    {#if editing}
        <div class="mx-auto w-11/12 lg:w-3/5">
            <CampaignEditor bind:entity={campaign} onSave={saveCampaign} onCancel={() => { editing = false; fetchCampaign(campaign.key); }} />
        </div>
    {:else}
        <StallView
            baseUrl={`campaigns/${campaignKey}`}
            bannerUrl={null}
            owner={campaign.owner}
            title={campaign.name} description={campaign.description}
            onEdit={campaign.is_mine ? (() => editing = true) : null}
            showItemsOwner={true}
            canAddItems={true}
            hasAuctions={true}
            hasListings={true} />
    {/if}
{/if}
