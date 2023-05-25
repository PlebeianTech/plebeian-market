<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { Info, token } from "$lib/stores";
    import { ErrorHandler, getUserNotifications, putUserNotifications } from "$lib/services/api";
    import { PostUserNotification, type UserNotification } from "$lib/types/notification";

    export let onSave: () => void = () => {};

    let userNotifictions: UserNotification[] = [];
    let modified = false;

    $: saveButtonActive = !saving && modified;

    let saving = false;
    function save() {
        saving = true;
        putUserNotifications($token, userNotifictions.map(n => new PostUserNotification(n.notificationType, n.action)),
        () => {
            saving = false;
            modified = false;
            Info.set("Your notification preferences have been saved!");
            onSave();
        },
        new ErrorHandler(true, () => saving = false));
    }

    onMount(async() => {
        getUserNotifications($token,
            notifications => {
                userNotifictions = notifications;
            }
        );
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>Notifications</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">Notifications</h2>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div>
        {#each userNotifictions as notification}
        <div class="form-control w-full max-w-xs">
            <label for="" class="label">
                <span class="label-text">{notification.notificationTypeDescription}</span>
            </label>
            <select bind:value={notification.action} on:change={() => modified = true} class="select select-bordered w-full max-w-xs">
                {#each notification.availableActions as availableAction}
                    <option value={availableAction.action}>{availableAction.description}</option>
                {/each}
            </select>
        </div>
        {/each}
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save-user-notifications" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={save}>Save</button>
</div>
