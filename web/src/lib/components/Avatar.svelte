<script lang="ts">
    import type { IAccount } from "$lib/types/user";

    export let account: IAccount;
    export let height = "8";
    export let showUsername = true;
    export let linkActive = true;

    $: href = account.usernameVerified ? `https://twitter.com/${account.username}` : null;
</script>

{#if linkActive}
    <a href={href}>
        <div class="avatar" class:verified={account.usernameVerified} class:not-verified={!account.usernameVerified}>
            <div class="w-{height} rounded-full border border-accent">
                <img src={account.profileImageUrl} alt="{account.username}'s avatar" />
            </div>
        </div>
    </a>
{:else}
    <div class="avatar" class:verified={account.usernameVerified} class:not-verified={!account.usernameVerified}>
        <div class="w-{height} rounded-full border border-accent">
            <img src={account.profileImageUrl} alt="{account.username}'s avatar" />
        </div>
    </div>
{/if}
{#if showUsername}
    <span class="font-bold">
        <a href={href}>{account.username}</a>
    </span>
{/if}