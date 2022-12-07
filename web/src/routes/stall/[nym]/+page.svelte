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

    let serverLoadedUser = data.serverLoadedUser;
</script>

{#if serverLoadedUser}
    <MetaTags
            title={serverLoadedUser.stall_name ?? (serverLoadedUser.nym ? serverLoadedUser.nym + "'s Stall" : "Check this Plebeian Market Campaign!")}
            description={serverLoadedUser.stall_description ?? serverLoadedUser.description ?? "Check the products at this Plebeian Market Stall!"}
            openGraph={{
                site_name: "Plebeian Market",
                type: "website",
                url: $page.url.href,
                title: serverLoadedUser.stall_name ?? (serverLoadedUser.nym ? serverLoadedUser.nym + "'s Stall" : "Check this Plebeian Market Campaign!"),
                description: serverLoadedUser.stall_description ?? serverLoadedUser.description ?? "Check the products at this Plebeian Market Stall!",
                images: [
                  {
                    url: serverLoadedUser.stall_banner_url ?? serverLoadedUser.profile_image_url ?? "",
                    alt: serverLoadedUser.stall_name ?? (serverLoadedUser.nym ? serverLoadedUser.nym + "'s Stall" : "Check this Plebeian Market Campaign!"),
                  }
                ],
            }}
            twitter={{
                site: import.meta.env.VITE_TWITTER_USER,
                handle: import.meta.env.VITE_TWITTER_USER,
                cardType: "summary_large_image",
                image: serverLoadedUser.stall_banner_url ?? serverLoadedUser.profile_image_url ?? "",
                imageAlt: serverLoadedUser.stall_name ?? (serverLoadedUser.nym ? serverLoadedUser.nym + "'s Stall" : "Check this Plebeian Market Campaign!"),
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
            editUrl={isMyStall ? "/settings#onsave=mystall" : null}
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
                    <a class="btn btn-primary" href="/">Home</a>
                </div>
            </div>
        </div>
    {/if}
{/if}