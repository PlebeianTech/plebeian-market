<script lang="ts">
    import { putConfigureDefaultBadges } from "$lib/services/api";

    export let onDefaultBadgesConfigured = () => {};

    function configureBadges() {
        putConfigureDefaultBadges(onDefaultBadgesConfigured);
    }
</script>

<h2 class="text-4xl text-center my-8">Welcome to your new site!</h2>
<div class="flex justify-center items-center mt-12 gap-4 flex-col">
    <p class="text-center text-2xl my-4 max-w-xl">
        Note: When setting up a new site, you need to define a reputation system to use!
    </p>
    <p class="text-center text-xl my-4 max-w-xl">
        We currently only support automatically importing <code>plebeian.market</code>'s reputation system ("skin in the game" badge),
        but in the future we will support importing reputation systems from other instances or starting from scratch!
    </p>
    <button class="btn btn-primary" on:click|preventDefault={configureBadges}>Use plebeian.market's reputation</button>
</div>
