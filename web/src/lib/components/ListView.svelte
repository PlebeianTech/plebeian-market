<script context="module" lang="ts">
    export enum ListViewStyle {
        List,
        Grid,
        Table
    }
</script>

<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { type ILoader, getEntities, postEntity, putEntity } from "$lib/services/api";
    import { token } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import Loading from "$lib/components/Loading.svelte";

    export let loader: ILoader;
    export let card;
    export let editor: any | null;
    export let showItemsOwner = false;
    export let showItemsCampaign = false;
    export let postEndpoint: string | null = null;
    export let style: ListViewStyle;

    export let columns: string[] = [];

    export let onSave: (key: string, entity: IEntity) => void = () => { };

    export let onForceReload = () => {};

    let currentEntity: IEntity | undefined;
    function setCurrent(entity: IEntity) {
        currentEntity = entity;
    }

    export let entities: IEntity[] | null = null;

    export function fetchEntities(successCB: () => void = () => {}) {
        getEntities(loader, $token,
            e => {
                entities = e;
                successCB();
            });
    }

    function saveCurrentEntity() {
        if (!currentEntity || !currentEntity.validate(true)) {
            return;
        }

        entities = null;

        if (currentEntity.key !== "") {
            putEntity($token, currentEntity,
                () => {
                    onSave(currentEntity!.key, currentEntity!);
                    fetchEntities(() => { currentEntity = undefined; })
                });
        } else {
            postEntity(postEndpoint, $token, currentEntity,
                (key) => {
                    onSave(key, currentEntity!);
                    fetchEntities(() => { currentEntity = undefined; });
                });
        }
    }

    function onEntityChanged() {
        entities = null;
        fetchEntities();
        onForceReload();
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    onMount(async () => {
        fetchEntities(() => { currentEntity = undefined; });
        interval = setInterval(fetchEntities, 10000);
    });

    onDestroy(() => {
        if (interval) {
            clearInterval(interval);
            interval = undefined;
        }
    });
</script>

<div class="mx-auto w-full">
    {#if currentEntity}
        <svelte:component this={editor} bind:entity={currentEntity} onSave={saveCurrentEntity} onCancel={() => currentEntity = undefined} />
    {:else if entities === null}
        <Loading />
    {:else}
        <slot name="new-entity" {setCurrent} />

        {#if style === ListViewStyle.List}
            {#each entities as entity}
                <svelte:component this={card} {entity} showOwner={showItemsOwner} showCampaign={showItemsCampaign} isEditable={editor !== null && entity.is_mine} onEdit={(e) => currentEntity = e} {onEntityChanged} />
            {/each}
        {:else if style === ListViewStyle.Grid}
            <div class="w-full">
                <div class="grid lg:grid-cols-2 gap-4">
                    {#each entities as entity}
                        <div class="">
                            <svelte:component this={card} {entity} showOwner={showItemsOwner} showCampaign={showItemsCampaign} isEditable={editor !== null && entity.is_mine} onEdit={(e) => currentEntity = e} {onEntityChanged} />
                        </div>
                    {/each}
                </div>
            </div>
        {:else if style === ListViewStyle.Table}
        <div class="overflow-x-auto w-full p-2">
            <table class="w-full">
                <thead class="bg-zinc-700/80">
                    {#each columns as column}
                        <th class="text-start text-blue-200 px-4 whitespace-nowrap py-4 text-sm uppercase">{column}</th>
                    {/each}
                </thead>
                <tbody class="w-full whitespace-nowrap">
                    {#each entities as entity}
                        <svelte:component this={card} {entity} isEditable={editor !== null && entity.is_mine} onEdit={(e) => currentEntity = e} {onEntityChanged} />
                    {/each}
                </tbody>
            </table>
        </div>
        {/if}
    {/if}
</div>
