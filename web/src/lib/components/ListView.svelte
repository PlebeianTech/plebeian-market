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
    import type { IEntity } from '$lib/types/base';
    import Loading from "$lib/components/Loading.svelte";

    export let loader: ILoader;
    export let card;
    export let editor: any | null;
    export let showNewButton: boolean = true;
    export let style: ListViewStyle;
    export let extraClasses: string = "w-11/12 lg:w-3/5";

    export let columns: string[] = [];

    export let newEntity: (() => IEntity) | undefined = undefined;
    export let onCreated: () => void = () => { };
    export let onForceReload = () => {};

    let currentEntity: IEntity | undefined;
    export let entities: IEntity[] | null = null;

    export function fetchEntities(successCB: () => void = () => {}) {
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

<div class="{extraClasses} mx-auto">
    {#if currentEntity}
        <svelte:component this={editor} bind:entity={currentEntity} onSave={saveCurrentEntity} onCancel={() => currentEntity = undefined} />
    {:else if entities === null}
        <Loading />
    {:else}
        <div>
            {#if showNewButton}
                <div class="mx-auto my-10 glowbutton glowbutton-new" on:click|preventDefault={() => currentEntity = newEntity !== undefined ? newEntity() : undefined}></div>
            {/if}
        </div>

        {#if style === ListViewStyle.List}
            {#each entities as entity}
                <svelte:component this={card} {entity} isEditable={editor !== null} onEdit={(e) => currentEntity = e} {onEntityChanged} />
            {/each}
        {:else if style === ListViewStyle.Grid}
            <div>
                <div class="grid grid-cols-1 md:grid-cols-3">
                    {#each entities as entity}
                        <div class="h-auto">
                            <svelte:component this={card} {entity} isEditable={editor !== null} onEdit={(e) => currentEntity = e} {onEntityChanged} />
                        </div>
                    {/each}
                </div>
            </div>
        {:else if style === ListViewStyle.Table}
            <div class="overflow-x-auto w-full">
                <table class="table w-full">
                    <thead>
                        {#each columns as column}
                            <th>{column}</th>
                        {/each}
                    </thead>
                    <tbody>
                        {#each entities as entity}
                            <svelte:component this={card} {entity} isEditable={editor !== null} onEdit={(e) => currentEntity = e} {onEntityChanged} />
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    {/if}
</div>
