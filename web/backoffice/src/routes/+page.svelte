<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { onMount } from 'svelte';
    import { login } from "$lib/utils";
    import { getBadges } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { token } from "$sharedLib/stores";
    import NewSite from "$lib/components/NewSite.svelte";
    import Onboarding from "$lib/components/Onboarding.svelte";
    import StallView from "$lib/components/StallView.svelte";
    import { requestLoginModal } from "$sharedLib/utils";

    function onLogin() {
        setTimeout(() => {token.set(localStorage.getItem("token"))}, 0);
    }

    let badges: null | Array<any> = null;

    async function refreshBadges() {
        badges = await getBadges();
    }

    onMount(async () => { refreshBadges(); });
</script>

{#if badges !== null && badges.length === 0}
    <NewSite onDefaultBadgesConfigured={refreshBadges} />
{:else}
    {#if $user}
        {#if $user.lightningAddress !== null && $user.lightningAddress !== "" && $user.stallName !== null && $user.stallName !== "" && $user.email !== null && $user.email !== "" && $user.emailVerified && $user.lnauthKeyName !== null}
            <StallView />
        {:else}
            <Onboarding />
        {/if}
    {:else}
        <h2 class="text-4xl text-center my-8">Stall Manager</h2>
        <div class="flex justify-center items-center mt-12 gap-4 flex-col">
            <a href={null} class="btn btn-primary btn-lg normal-case" on:click={async () => requestLoginModal(() => {}, onLogin)} on:keypress={async () => requestLoginModal(() => {}, onLogin)}><b>Login using Nostr</b></a>
            <a href={null} class="btn btn-primary btn-lg normal-case" on:click={() => login()} on:keypress={() => login()}><b>Login using Lightning</b></a>
        </div>
    {/if}
{/if}
