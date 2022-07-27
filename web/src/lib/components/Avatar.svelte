<script lang="ts">
    import type { IAccount } from "$lib/types/user";
    export let account: IAccount;
    $: href = account.usernameVerified ? `https://twitter.com/${account.username}` : null;
</script>

<a href={href}>
    <div class="avatar" class:verified={account.usernameVerified} class:not-verified={!account.usernameVerified}>
        <div class="w-8 rounded-full">
            <img src={account.profileImageUrl} alt="{account.username}'s avatar" />
        </div>
    </div>
</a>
<span class="font-bold">
    <a href={href}>{account.username}</a>
</span>