<script context="module" lang="ts">
    export enum AvatarSize {
        S,
        M,
        L
    }
</script>

<script lang="ts">
    import type { IAccount } from "$lib/types/user";

    export let account: IAccount;
    export let size: AvatarSize = AvatarSize.S;
    export let inline = false;
    export let nymOnly = true;
</script>

<a rel="external" class="link" href="/stall/{account.nym}">
    <div class="" class:flex-col={!inline} class:flex-row={inline}>
        <div class="flex space-x-2">
            <div class="avatar" class:verified={account.twitterUsernameVerified} class:not-verified={!account.twitterUsernameVerified}>
                <div class="rounded-full" class:w-8={size === AvatarSize.S} class:w-12={size === AvatarSize.M} class:w-24={size === AvatarSize.L}>
                    <img src={account.profileImageUrl} alt="{account.nym}'s avatar" />
                </div>
            </div>
            <div class="font-bold flex items-center justify-center" class:text-2xl={size === AvatarSize.L}>
                {#if nymOnly}
                    {account.nym}
                {:else}
                    {account.displayName}
                {/if}
            </div>
        </div>
    </div>
</a>
