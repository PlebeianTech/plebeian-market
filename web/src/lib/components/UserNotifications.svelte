<script lang="ts">
    import { Info, token, user } from "../stores";
    import { ErrorHandler, getUserNotifications, putUserNotifications } from "../services/api";
    import { PostUserNotification, type UserNotification } from "../types/notification";

    let userNotifictions: UserNotification[] = [];

    export function show() {
        getUserNotifications($token,
            notifications => {
                userNotifictions = notifications;
                let toggle = <HTMLInputElement>document.getElementById('user-notifications-toggle');
                if (toggle) {
                    toggle.checked = true;
                }
            }
        );
    }

    let saving = false;
    function save() {
        saving = true;
        putUserNotifications($token, userNotifictions.map(n => new PostUserNotification(n.notificationType, n.action)),
        () => {
            saving = false;
            Info.set("Your notification preferences have been saved!");
            hide();
        },
        new ErrorHandler(true, () => saving = false));
    }

    function hide() {
        let toggle = <HTMLInputElement>document.getElementById('user-notifications-toggle');
        if (toggle) {
            toggle.checked = false;
        }
    }
</script>

<input type="checkbox" id="user-notifications-toggle" for="user-notifications" class="modal-toggle" />
<div class="modal">
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-1xl">
        <label for="user-notifications-modal" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={hide}>✕</label>
        <div class="mt-4 w-full">
            {#each userNotifictions as notification}
            <div class="form-control w-full max-w-xs">
                <label for="" class="label">
                    <span class="label-text">{notification.notificationTypeDescription}</span>
                </label>
                <select bind:value={notification.action} class="select select-bordered w-full max-w-xs">
                    {#each notification.availableActions as availableAction}
                        <option value={availableAction.action}>{availableAction.description}</option>
                    {/each}
                </select>
            </div>
            {/each}
            <div class="flex justify-center items-center mt-4 h-15">
                {#if saving}
                    <button class="btn" disabled>Save</button>
                {:else}
                    <div id="save-user-notifications" class="glowbutton glowbutton-save" on:click|preventDefault={save}></div>
                {/if}
            </div>
        </div>
    </div>
</div>