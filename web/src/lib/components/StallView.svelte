<script lang="ts">
    import AuctionCard from "$lib/components/AuctionCard.svelte";
    import type { IAccount, User } from "../types/user";
    import { type ILoader, getEntities, getStall, getProfile, ErrorHandler, postEntity, putEntity } from "../services/api";
    import { onMount } from "svelte";
    import { token, user } from "../stores";
    import StallNotFound from "./StallNotFound.svelte";
    import { afterNavigate } from '$app/navigation';
    import type { IEntity } from '$lib/types/base';
    import Loading from "$lib/components/Loading.svelte";
    import Avatar from "$lib/components/Avatar.svelte";
    import { goto } from '$app/navigation';

    export let title;
    export let card;
    export let editor;
    export let stallOwnerNym;
    export let showNewButton: boolean = true;
    export let loader: ILoader;
    export let entities: IEntity[] | null = null;

    export let newEntity: () => IEntity;
    export let onView: (entity: IEntity) => void = (_) => { };
    export let onCreated: () => void = () => { };

    let stallOwner: User;
    let storeAccount: IAccount;
    let currentTab = "ACTIVE AUCTIONS";
    let tabList = ['ACTIVE AUCTIONS', 'PAST AUCTIONS']
    let loading = true;
    let currentEntity: IEntity | undefined;

    function fetchProfile(tokenValue) {
        getProfile(tokenValue,
            u => {
                user.set(u);
                // if user and no stallNym -> go to own stall
                if (stallOwnerNym === "") {
                    goto(`/stall/${u.nym}`);
                }
            });
    }

    function fetchStall(stallOwnerNym: string) {
        getStall(stallOwnerNym, 
            s => {
                stallOwner = s;
                storeAccount = {
                    username: stallOwner.twitter.username,
                    profileImageUrl: stallOwner.twitter.profileImageUrl,
                    usernameVerified: stallOwner.twitter.usernameVerified,
                }
                loading = false;
                if ($user && $user.nym === stallOwner.nym) {
                    tabList = ["UNLAUNCHED"].concat(tabList);
                    currentTab = "UNLAUNCHED";
                }
            }, 
            new ErrorHandler(false, () => {
                loading = false;
            }));
    }

    function fetchEntities(successCB: () => void = () => {}) {
        getEntities(loader, $token,
            e => {
                entities = e;
                successCB();
            }, 
            new ErrorHandler(false, () => {}));
    }

    function onDelete() {
        entities = null;
        fetchEntities();
    }

    function saveCurrentEntity() {
        if (!currentEntity || !currentEntity.validate()) {
            return;
        }

        entities = null;

        if (currentEntity.key !== "") {
            putEntity($token, currentEntity,
                () => {
                    fetchEntities(() => { currentEntity = undefined; })
                });
        } else {
            postEntity($token, currentEntity,
                () => {
                    onCreated();
                    fetchEntities(() => { currentEntity = undefined; });
                });
        }
    }

    afterNavigate(() => {
        if (stallOwnerNym !== "") {
            fetchStall(stallOwnerNym);
            fetchEntities();
        }
    });

    onMount(async () => {
        fetchProfile($token);
    });
</script>


<svelte:head>
    <title>{title}</title>
</svelte:head>

{#if loading}
    <!-- Show loading spinner until storeOwner is loaded -->
    <div class="hero h-5/6 bg-base-200">
        <div class="hero-content text-center">
            <div class="max-w-md">
                <div class="lds-ring accent"><div></div><div></div><div></div><div></div></div>
            </div>
        </div>
    </div>
{:else}
    {#if stallOwner || stallOwnerNym === "" && $user}
        <div class="w-full md:w-1/2 mx-auto mt-4">
            <div class="mx-auto">
                <!-- top profile section -->
                <div class="flex items-center justify-between mb-4">
                    <div class="flex-none lg:h-32 lg:w-32 w-12 h-12 mx-4">
                        <Avatar account={storeAccount} showUsername={false} height="32" />
                    </div>
                </div>
                <span class="font-thin text-3xl mx-4">
                    @{stallOwner.nym}
                </span>
                {#if entities === null || entities.length === 0}
                    <div class="mt-4 mx-4 font-thin text-xl mb-4">
                        User is not selling anything
                    </div>
                {:else}
                    <div class="flex justify-between md:justify-start md:mx-4 mt-4 mx-8">
                        <span class="text-sm font-semibold md:mr-4">{stallOwner.runningAuctionCount} Active Auctions</span>
                        <span class="text-sm font-semibold">{stallOwner.endedAuctionCount} Past Auctions</span>
                    </div>
                {/if}
            </div>
        </div>
        <!-- if stallOwner viewing own stall -->
        {#if $user && $user.nym == stallOwner.nym}
        <div>
            <div class="pt-10 flex justify-center items-center">
                <section class="w-11/12 lg:w-3/5">
                    {#if currentEntity}
                        <svelte:component this={editor} bind:entity={currentEntity} onSave={saveCurrentEntity} onCancel={() => currentEntity = undefined} />
                    {:else if entities === null}
                        <Loading />
                    {:else}
                        {#if showNewButton}
                            <div class="flex items-center justify-center mb-4">
                                <div class="glowbutton glowbutton-new" on:click|preventDefault={() => currentEntity = newEntity()}></div>
                            </div>
                        {/if}
                    {/if}
                </section>
            </div>
        </div>
        {/if}
        {#if entities !== null && entities.length > 0}
        <!-- stallOwner listing section -->
        <hr class="border-solid border-accent divide-y-0 opacity-50 my-5">
        <div class="tabs flex items-center justify-center">
            {#each tabList as tab}
                <li class="tab text-xs font-semibold" class:tab-active={tab === currentTab} class:tab-bordered={tab === currentTab} on:click={() => currentTab = tab}>
                    <div>{tab}</div>
                </li>
            {/each}
        </div>
        <div class="pt-6 pb-6">
            <div class="grid md:grid-cols-3 grid-cols-1">
                    {#each entities as entity}
                        {#if $user && $user.nym == stallOwner.nym}
                            {#if currentTab === 'UNLAUNCHED' && !entity.started && !entity.ended}
                                <div class="h-auto">
                                    <svelte:component this={AuctionCard} {entity} onEdit={(e) => currentEntity = e} {onView} {onDelete} />
                                </div>
                            {/if}
                        {/if}
                        {#if currentTab === 'ACTIVE AUCTIONS' && entity.started && !entity.ended}
                            <div class="h-auto">
                                {#if card===AuctionCard}
                                    <svelte:component this={card} {entity} onEdit={(e) => currentEntity = e} {onView} {onDelete} />
                                {:else}
                                    <svelte:component this={card} auction={entity} />
                                {/if}
                            </div>
                        {/if}
                        {#if currentTab === 'PAST AUCTIONS' && entity.ended}
                            <div class="h-auto">
                                {#if card===AuctionCard}
                                    <svelte:component this={card} {entity} onEdit={(e) => currentEntity = e} {onView} {onDelete} />
                                {:else}
                                    <svelte:component this={card} auction={entity} />
                                {/if}
                            </div>
                        {/if}
                    {/each}
            </div>
        </div>
        {/if}
    {:else}
        <StallNotFound />
    {/if}
{/if}
