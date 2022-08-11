<script lang="ts">
    import Avatar from "$lib/components/Avatar.svelte";
    import type { User } from "../types/user";

    export let profileUser: User;
    export let showDivider = true;

</script>


<div class="w-full md:w-1/2 mx-auto mt-5">
    <div class="mx-auto">
        <div class="flex items-center justify-between mb-4">
            <div class="flex-none lg:h-32 lg:w-32 w-12 h-12 mx-4">
                <Avatar account={profileUser.twitter} showUsername={false} height="32" />
            </div>
        </div>
        <span class="font-thin text-3xl mx-4">
            @{profileUser.nym}
        </span>
    </div>
</div>
{#if showDivider}
    <hr class="w-2/3 mx-auto border-solid border-accent divide-y-0 opacity-50 my-5">
{/if}
