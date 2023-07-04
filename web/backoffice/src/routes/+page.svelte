<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import { getBaseUrl } from "../lib/utils";
    import type { User } from "$lib/types/user";
    import { getProfile, ErrorHandler } from "$lib/services/api";
    import { token } from "$lib/stores";
    import StallView from "$lib/components/StallView.svelte";

    let owner: User | null = null;
    let loading = true;

    function fetchStall(nym: string) {
        loading = true;
        getProfile($token, nym,
            s => {
                owner = s;
                loading = false;
            },
            new ErrorHandler(false, () => {
                loading = false;
            }));
    }

    const tokenUnsubscribe = token.subscribe((t) => {
        if (t) {
            fetchStall('me');
        }
    });
    onDestroy(tokenUnsubscribe);

    onMount(async () => {
        if ($token) {
            fetchStall('me');
        }
    });
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

{#if owner}
    <StallView
        baseUrl="users/me"
        bannerUrl={null}
        {owner} title={null}
        description={null}
        editUrl="/admin/account/settings#onsave=mystall"
        badges={owner.badges}
        isOwnStall={true}
        showItemsOwner={false}
        showItemsCampaign={true}
        canAddItems={true}
        showActiveAuctions={true} showPastAuctions={true}
        showActiveListings={true} showPastListings={true} />
{/if}
