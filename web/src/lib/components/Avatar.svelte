<script lang="ts">
    import type { IAccount } from "$lib/types/user";
    export let account: IAccount;
</script>

<div class="avatar" class:verified={account.usernameVerified} class:not-verified={!account.usernameVerified}>
    <div class="w-8 rounded-full">
        <img src={account.profileImageUrl} alt="{account.username}'s avatar" />
    </div>
</div>
<span class="font-bold">
    {#if account.usernameVerified}
        <a href="https://twitter.com/{account.username}">{account.username}</a>
    {:else}
        {account.username}
    {/if}
</span>