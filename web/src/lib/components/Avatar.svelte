<script lang="ts">
    import type { IAccount } from "$lib/types/user";

    export let account: IAccount;
    export let height = "8";
</script>

<a rel="external" class="link" href="/stall/{account.nym}">
    <div class="flex flex-col">
        <div>
            <div class="avatar" class:verified={account.twitterUsernameVerified} class:not-verified={!account.twitterUsernameVerified}>
                <div class="w-{height} rounded-full">
                    <img src={account.profileImageUrl} alt="{account.nym}'s avatar" />
                </div>
            </div>
        </div>
        <span class="font-bold">
            {account.nym}
        </span>
    </div>
</a>
