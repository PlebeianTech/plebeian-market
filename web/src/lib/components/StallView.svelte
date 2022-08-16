<script lang="ts">
    import { onMount } from 'svelte';
    import AuctionCard from "$lib/components/AuctionCard.svelte";
    import StallNotFound from "$lib/components/StallNotFound.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import ProfileCard from "./ProfileCard.svelte";
    import ListView from "$lib/components/ListView.svelte";
    import PublicAuctionCard from "$lib/components/PublicAuctionCard.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import type { User } from "$lib/types/user";
    import { getProfile, ErrorHandler } from "$lib/services/api";
    import { token, user } from "$lib/stores";
    import { Auction, fromJson } from "$lib/types/auction";

    export let stallOwnerNym;

    let stallOwner: User;
    let currentTab: number | null = null;
    let loading = true;

    $: isMyStall = $user && stallOwner && $user.nym === stallOwner.nym;
    $: tabList = isMyStall ?
        ["NEW AUCTIONS", "ACTIVE AUCTIONS", "PAST AUCTIONS"] :
        ["ACTIVE AUCTIONS", "PAST AUCTIONS"];
    $: cardType = isMyStall ? AuctionCard : PublicAuctionCard;
    $: showAsGrid = !(isMyStall);

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
        if (stallOwnerNym !== "") {
            fetchStall(stallOwnerNym);
        }
    });
</script>

{#if loading}
    <Loading />
{:else}
    {#if stallOwner}
        <ProfileCard profileUser={stallOwner} />
        <div class="tabs flex items-center justify-center">
            {#each tabList as tab, i}
                <li class="tab text-xs font-semibold"
                    class:tab-active={currentTab === null ? i === 0 : i === currentTab}
                    class:tab-bordered={currentTab === null ? i === 0 : i === currentTab}
                    on:click={() => currentTab = i}>
                    <div>{tab}</div>
                </li>
            {/each}
        </div>
        <div class="pt-6 pb-6">
            {#if currentTab === null ? isMyStall : currentTab === tabList.length - 3}
                <div class="h-auto">
                    <ListView
                        title="{stallOwner.nym}'s Stall"
                        loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=new`, responseField: 'auctions', fromJson}}
                        newEntity={() => new Auction()}
                        editor={AuctionEditor}
                        showNewButton={true}
                        card={AuctionCard}
                        showAsGrid={false} />
                </div>
            {:else if currentTab === null ? !isMyStall : currentTab === tabList.length - 2}
                <div class="h-auto">
                    <ListView
                        title="{stallOwner.nym}'s Stall"
                        loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=running`, responseField: 'auctions', fromJson}}
                        editor={null}
                        showNewButton={false}
                        card={cardType}
                        showAsGrid={showAsGrid} />
                </div>
            {:else if currentTab === tabList.length - 1}
                <div class="h-auto">
                    <ListView
                        title="{stallOwner.nym}'s Stall"
                        loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=ended`, responseField: 'auctions', fromJson}}
                        editor={null}
                        showNewButton={false}
                        card={cardType}
                        showAsGrid={showAsGrid} />
                </div>
            {/if}
        </div>
    {:else}
        <StallNotFound />
    {/if}
{/if}
