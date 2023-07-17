<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import { getBaseUrl } from "../lib/utils";
    import { user } from "$lib/stores";
    import StallView from "$lib/components/StallView.svelte";
</script>

<MetaTags
        title="Plebeian Market"
        description="Plebeian Market is a distributed self sovereign P2P market place."
        openGraph={{
            site_name: import.meta.env.VITE_SITE_NAME,
            type: "website",
            url: $page.url.href,
            title: "Plebeian Market",
            description: "Plebeian Market is a distributed self sovereign P2P market place.",
            images: [
              {
                url: getBaseUrl() + "images/Plebeian_Logo_OpenGraph.png",
                alt: "Plebeian Market logo"
              }
            ],
        }}
        twitter={{
            site: import.meta.env.VITE_TWITTER_USER,
            handle: import.meta.env.VITE_TWITTER_USER,
            cardType: "summary_large_image",
            image: getBaseUrl() + "images/Plebeian_Logo_OpenGraph.png",
            imageAlt: "Plebeian Market logo",
        }}
/>

{#if $user}
    <StallView
        baseUrl="users/me"
        owner={$user} title={null}
        description={null}
        isOwnStall={true}
        showItemsCampaign={true}
        canAddItems={true}
        showActiveAuctions={true} showPastAuctions={true}
        showActiveListings={true} showPastListings={true} />
{/if}
