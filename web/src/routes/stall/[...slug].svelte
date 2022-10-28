<svelte:head>
    <title>Market Stall</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { stallOwnerNym: slug } }
    }
</script>

<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from "$app/navigation";
    import Loading from "$lib/components/Loading.svelte";
    import StallView from "$lib/components/StallView.svelte";
    import type { User } from "$lib/types/user";
    import { getProfile, ErrorHandler } from "$lib/services/api";
    import { token, user } from "$lib/stores";

    export let stallOwnerNym: string;

    let owner: User | null = null;
    let loading = false;

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
        if (stallOwnerNym === "" || stallOwnerNym === null) {
            goto("/");
        } else {
            fetchStall(stallOwnerNym);
        }
    });
</script>

{#if loading}
    <Loading />
{:else}
    {#if owner}
        <StallView
            baseUrl={`users/${isMyStall ? 'me' : owner.nym}`}
            bannerUrl={owner.stallBannerUrl}
            {owner} {title} description={owner.stallDescription}
            onEdit={isMyStall ? () => { goto("/settings#onsave=mystall") } : null}
            isOwnStall={isMyStall}
            showItemsOwner={false} showItemsCampaign={true}
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