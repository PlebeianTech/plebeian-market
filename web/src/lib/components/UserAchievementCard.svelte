<script lang="ts">
    import { deleteEntity } from "$lib/services/api";
    import { token } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import type { UserAchievement } from '$lib/types/user';
    import { getMonthName } from '$lib/utils';

    // svelte-ignore unused-export-let
    export let isEditable = false;
    // svelte-ignore unused-export-let
    export let showCampaign = false;
    // svelte-ignore unused-export-let
    export let showOwner = false;

    export let entity: IEntity;
    $: achievement = <UserAchievement>(<unknown>entity);

    export let onEdit = (_: UserAchievement) => {};
    export let onEntityChanged = () => {};

    function del() {
        if (window.confirm("Are you sure?")) {
            deleteEntity($token, entity, onEntityChanged);
        }
    }
</script>

<div class="">
    <div class="card md:card-side bg-base-300 max-w-full overflow-hidden shadow-xl my-3">
        <div class="card-body">
            <div>
                <p class="whitespace-nowrap">
                    {#if achievement.from_year || achievement.from_month}
                        From {achievement.from_year} {#if achievement.from_month}({getMonthName(achievement.from_month)}){/if}
                    {/if}
                    {#if achievement.to_year || achievement.to_month}
                        to {achievement.to_year} {#if achievement.to_month}({getMonthName(achievement.to_month)}){/if}
                    {/if}
                </p>
                <p class="text-2xl mt-2">
                    {achievement.achievement}
                </p>
            </div>
            <div class="mt-2 card-actions justify-end">
                <button class="btn mx-1" on:click={() => onEdit(achievement)}>Edit</button>
                <button class="btn mx-1" on:click={del}>Delete</button>
            </div>
        </div>
    </div>
</div>
