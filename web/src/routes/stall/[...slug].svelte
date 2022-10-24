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
    import { token, user, Info } from "$lib/stores";

    export let stallOwnerNym: string;

    let stallOwner: User | null = null;
    let loading = true;

    $: title = stallOwner ? (stallOwner.stallName !== null ? stallOwner.stallName : `${stallOwner.nym}'s Stall`) : "";
    $: isMyStall = stallOwner !== null && $user !== null && stallOwner.nym === $user.nym;

    function fetchStall(stallOwnerNym: string) {
        loading = true;
        getProfile($token, stallOwnerNym,
            s => {
                stallOwner = s;
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
    {#if stallOwner}
        <StallView
            baseUrl={`users/${isMyStall ? 'me' : stallOwner.nym}`}
            bannerUrl={stallOwner.stallBannerUrl}
            owner={stallOwner}
            {title} description={stallOwner.stallDescription}
            onEdit={isMyStall ? () => { goto("/settings#onsave=mystall") } : null}
            showItemsOwner={false} showItemsCampaign={true}
            canAddItems={isMyStall}
            hasAuctions={stallOwner.hasAuctions}
            hasListings={stallOwner.hasListings} />
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