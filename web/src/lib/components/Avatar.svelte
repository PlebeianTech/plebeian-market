<script lang="ts">
    import type { IAccount } from "$lib/types/user";

    export let account: IAccount;
    export let height = "8";
    export let inline = false;
    export let nymOnly = false;
</script>

<a rel="external" class="link" href="/stall/{account.nym}">
    <div class="flex gap-2" class:flex-col={!inline} class:flex-row={inline}>
        <div>
            <div class="avatar" class:verified={account.twitterUsernameVerified} class:not-verified={!account.twitterUsernameVerified}>
                <div class="w-{height} rounded-full">
                    <img src={account.profileImageUrl} alt="{account.nym}'s avatar" />
                </div>
            </div>
        </div>
        <span class="font-bold flex items-center justify-center">
            {#if nymOnly}
                {account.nym}
            {:else}
                {account.displayName}
            {/if}
        </span>
    </div>
</a>
