<script lang="ts">
    import type { IAccount } from "$lib/types/user";

    export let account: IAccount;
    export let height = "8";
    export let showUsername = true;
</script>

<div class="avatar" class:verified={account.usernameVerified} class:not-verified={!account.usernameVerified}>
    <div class="w-{height} rounded-full">
        <img src={account.profileImageUrl} alt="{account.username}'s avatar" />
    </div>
</div>

{#if showUsername}
    <span class="font-bold">
        <a class="link" href="/stall/{account.username}">{account.username}</a>
    </span>
{/if}