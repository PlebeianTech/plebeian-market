<script lang="ts">
    import AuctionCard from "$lib/components/AuctionCard.svelte";
    import StallNotFound from "$lib/components/StallNotFound.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import ProfileCard from "./ProfileCard.svelte";
    import ListView from "$lib/components/ListView.svelte";
    import PublicAuctionCard from "$lib/components/PublicAuctionCard.svelte";
    import AuctionEditor from "$lib/components/AuctionEditor.svelte";
    import type { User } from "$lib/types/user";
    import { getStall, ErrorHandler } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { afterNavigate } from '$app/navigation';
    import { Auction, fromJson } from "$lib/types/auction";

    export let stallOwnerNym;

    let stallOwner: User;
    let currentTab = "ACTIVE AUCTIONS";
    let tabList;
    let loading = true;
    let cardType;
    let showAsGrid;

    function fetchStall(stallOwnerNym: string) {
        getStall(stallOwnerNym, 
            s => {
                stallOwner = s;
                loading = false;
                if ($user && $user.nym === stallOwner.nym) {
                    cardType = AuctionCard;
                    showAsGrid = false;
                    tabList = ["NEW AUCTIONS"].concat(tabList);
                    currentTab = "NEW AUCTIONS";
                } else {
                    cardType = PublicAuctionCard;
                    showAsGrid = true;
                }
            }, 
            new ErrorHandler(false, () => {
                loading = false;
            }));
    }

    afterNavigate(() => {
        tabList = ['ACTIVE AUCTIONS', 'PAST AUCTIONS']
        if (stallOwnerNym !== "") {
            fetchStall(stallOwnerNym);
        }
    });
</script>

{#if loading}
    <Loading />
{/if}

{#if stallOwner && !loading}
    <ProfileCard profileUser={stallOwner} />
    <div class="tabs flex items-center justify-center">
        {#each tabList as tab}
            <li class="tab text-xs font-semibold" class:tab-active={tab === currentTab} class:tab-bordered={tab === currentTab} on:click={() => currentTab = tab}>
                <div>{tab}</div>
            </li>
        {/each}
    </div>
    <div class="pt-6 pb-6">
        {#if currentTab === 'NEW AUCTIONS'}
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
        {:else if currentTab === 'ACTIVE AUCTIONS'}
            <div class="h-auto">
                <ListView
                    title="{stallOwner.nym}'s Stall"
                    loader={{endpoint: `users/${stallOwner.nym}/auctions?filter=running`, responseField: 'auctions', fromJson}}
                    editor={null}
                    showNewButton={false}
                    card={cardType}
                    showAsGrid={showAsGrid} />
            </div>
        {:else if currentTab === 'PAST AUCTIONS'}
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
