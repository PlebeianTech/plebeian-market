<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { type ILoader, getEntities, postEntity, putEntity } from "$lib/services/api";
    import { token } from "$lib/stores";
    import type { IEntity } from '$lib/types/base';
    import Loading from "$lib/components/Loading.svelte";
    import MetaTags from './MetaTags.svelte';

    export let title;

    export let loader: ILoader;
    export let newEntity: () => IEntity;

    export let card;
    export let editor;
    export let showNewButton: boolean = true;

    export let onCreated: () => void = () => { };
    export let onView: (entity: IEntity) => void = (_) => { };

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
    <MetaTags {title} />
</svelte:head>

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

            {#each entities as entity}
                <svelte:component this={card} {entity} onEdit={(e) => currentEntity = e} {onView} {onDelete} />
            {/each}
        {/if}
    </section>
</div>