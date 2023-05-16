<svelte:head>
    <title>Market Stall</title>
</svelte:head>

<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from "$app/navigation";
    import Loading from "$lib/components/Loading.svelte";
    import StallView from "$lib/components/StallView.svelte";
    import type { User } from "$lib/types/user";
    import { getProfile, ErrorHandler } from "$lib/services/api";
    import { token, user } from "$lib/stores";
    import { MetaTags } from "svelte-meta-tags";
    import { page } from "$app/stores";
    import {getShortTitle, getShortDescription} from "$lib/utils";

    /** @type {import('./$types').PageData} */
    export let data;

    let owner: User | null = null;
    let loading = true;

    $: title = owner ? (owner.stallName !== null ? owner.stallName : `${owner.nym}'s Stall`) : "";
    $: isMyStall = owner !== null && $user !== null && owner.nym === $user.nym;
    $: showActiveAuctions = isMyStall ? $user!.hasActiveAuctions : (owner ? owner.hasActiveAuctions : false);
    $: showPastAuctions = isMyStall ? $user!.hasPastAuctions : (owner ? owner.hasPastAuctions : false);
    $: showActiveListings = isMyStall ? $user!.hasActiveListings : (owner ? owner.hasActiveListings : false);
    $: showPastListings = isMyStall ? $user!.hasPastListings : (owner ? owner.hasPastListings : false);

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

    onMount(async () => {
        if (data.stallOwnerNym === "" || data.stallOwnerNym === null) {
            goto("/");
        } else {
            fetchStall(data.stallOwnerNym);
        }
    });

    let stallTitle: string = '';
    let stallDescription: string = '';

    let serverLoadedUser = data.serverLoadedUser;
    if (serverLoadedUser) {
        stallTitle = serverLoadedUser.stall_name ? getShortTitle(serverLoadedUser.stall_name) : serverLoadedUser.nym + "'s Stall";
        stallDescription = serverLoadedUser.stall_description ? getShortDescription(serverLoadedUser.stall_description) : "Check out my Plebeian Market stall!"
    }
</script>

{#if serverLoadedUser}
    <MetaTags
            title={stallTitle}
            description={stallDescription}
            openGraph={{
                site_name: import.meta.env.VITE_SITE_NAME,
                type: "website",
                url: $page.url.href,
                title: stallTitle,
                description: stallDescription,
                images: [
                  {
                    url: serverLoadedUser.stall_banner_url ?? serverLoadedUser.profile_image_url ?? "",
                    alt: stallTitle,
                  }
                ],
            }}
            twitter={{
                site: import.meta.env.VITE_TWITTER_USER,
                handle: import.meta.env.VITE_TWITTER_USER,
                cardType: "summary_large_image",
                image: serverLoadedUser.stall_banner_url ?? serverLoadedUser.profile_image_url ?? "",
                imageAlt: stallTitle,
            }}
    />
{/if}

{#if loading}
    <Loading />
{:else}
    {#if owner}
        <StallView
            baseUrl={`users/${isMyStall ? 'me' : owner.nym}`}
            bannerUrl={owner.stallBannerUrl}
            {owner} {title}
            description={owner.stallDescription}
            editUrl={isMyStall ? "/account/settings#onsave=mystall" : null}
            badges={owner.badges}
            isOwnStall={isMyStall}
            showItemsOwner={false}
            showItemsCampaign={true}
            canAddItems={isMyStall}
            {showActiveAuctions} {showPastAuctions}
            {showActiveListings} {showPastListings} />
    {:else}
        <div class="hero min-h-screen">
            <div class="hero-content text-center">
                <div class="max-w-md">
                    <h1 class="text-5xl font-bold">Stall Not Found</h1>
                    <p class="py-6">The stall you are looking for does not exist</p>
                    <a class="btn btn-primary" href="/web/backoffice/static">Home</a>
                </div>
            </div>
        </div>
    {/if}
{/if}
