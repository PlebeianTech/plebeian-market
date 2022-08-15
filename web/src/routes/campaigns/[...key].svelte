<script context="module">
    export async function load({ params }) {
        const { key } = params;
        return { props: { campaignKey: key } }
    }
</script>

<script lang="ts">
    import { Campaign, fromJson } from "$lib/types/campaign";
    import CampaignCard from "$lib/components/CampaignCard.svelte";
    import CampaignEditor from "$lib/components/CampaignEditor.svelte";
    import ListView from "$lib/components/ListView.svelte";

    export let campaignKey;
</script>

{#if campaignKey === ""}
    <ListView
        title="My Campaigns"
        loader={{endpoint: 'campaigns', responseField: 'campaigns', fromJson}} newEntity={() => new Campaign()}
        card={CampaignCard} editor={CampaignEditor}>
    </ListView>
{:else}
    <p>TODO: view campaign!</p>
{/if}