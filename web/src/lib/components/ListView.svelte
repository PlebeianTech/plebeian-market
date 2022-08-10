<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { type ILoader, getEntities, postEntity, putEntity } from "$lib/services/api";
    import { token } from "$lib/stores";
    import type { IEntity } from '$lib/types/base';
    import Loading from "$lib/components/Loading.svelte";

    export let title;
    export let loader: ILoader;
    export let card;
    export let editor: any | null;
    export let showNewButton: boolean = true;
    export let showAsGrid = false;

    export let newEntity: () => IEntity | undefined;
    export let onCreated: () => void = () => { };
    export let onView: (entity: IEntity) => void = (_) => { };

    // NB: the "new" button is shown when there are no auctions that are not ended and not viewed
    // (basically auctions that have been just created and the user didn't go through the whole tweet-start-view flow, *unless* they already ended)
    // $: showNewButton = ($user && $user.nym === stallOwnerNym || stallOwnerNym === "") || auctions === null || !auctions.find(a => !a.ended && viewedAuctions.indexOf(a.key) === -1);


    let currentEntity: IEntity | undefined;
    export let entities: IEntity[] | null = null;

    function fetchEntities(successCB: () => void = () => {}) {
        getEntities(loader, $token,
            e => {
                entities = e;
                successCB();
            });
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

    function onDelete() {
        entities = null;
        fetchEntities();
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    onMount(async () => {
        fetchEntities(() => { currentEntity = entities && entities.length === 0 ? newEntity() : undefined; });
        interval = setInterval(fetchEntities, 10000);
    });

    onDestroy(() => {
        if (interval) {
            clearInterval(interval);
            interval = undefined;
        }
    });
</script>

<svelte:head>
    <title>{title}</title>
</svelte:head>

<div class="w-11/12 lg:w-3/5 mx-auto">
    {#if currentEntity}
        <svelte:component this={editor} bind:entity={currentEntity} onSave={saveCurrentEntity} onCancel={() => currentEntity = undefined} />
    {:else if entities === null}
        <Loading />
    {:else}
        {#if showNewButton}
            <div class="mx-auto my-10 glowbutton glowbutton-new" on:click|preventDefault={() => currentEntity = newEntity()}></div>
        {/if}

        {#if !showAsGrid}
            {#each entities as entity}
                <svelte:component this={card} {entity} onEdit={(e) => currentEntity = e} {onView} {onDelete} />
            {/each}
        {/if}
    {/if}
</div>

<!-- Shows list as a grid on larger screens -->
{#if !currentEntity && showAsGrid && entities !== null}
<div>
    <div class="grid grid-cols-1 md:grid-cols-3">
        {#each entities as entity}
            <div class="h-auto">
                <svelte:component this={card} {entity} onEdit={(e) => currentEntity = e} {onView} {onDelete} />
            </div>
        {/each}
    </div>
</div>
{/if}