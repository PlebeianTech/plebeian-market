<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import LnurlAuth from "$lib/components/auth/Lnurl.svelte";
    import { AuthBehavior } from "$lib/stores";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";

    const dispatch = createEventDispatcher();

    export let onLogin = () => {};

    enum Provider {
        Lnurl
    }

    export let behavior;

    let provider = Provider.Lnurl;

    onMount(() => { provider = Provider.Lnurl });
</script>

<div class="w-full flex items-center justify-center mt-4">
    <div class="tabs tabs-boxed">
        <a class="tab tab-lg" class:tab-active={provider === Provider.Lnurl} href={null} on:click={() => provider = Provider.Lnurl}>Lightning</a>
    </div>
</div>

{#if behavior === AuthBehavior.Login}
    <h2 class="text-2xl text-center mt-10">Login to Plebeian Market Stall Manager</h2>
{:else}
    <h2 class="text-2xl text-center mt-10">Sign up for Plebeian Market Stall Manager</h2>
{/if}

{#if provider === Provider.Lnurl}
    <LnurlAuth {behavior} {onLogin} on:login={(_) => dispatch('login', {})} />
{/if}

<InfoBox>
    <div class="text-center">
        {#if behavior === AuthBehavior.Login}
            <p>New user? Please click <a class="link" href={null} on:click={() => behavior = AuthBehavior.Signup}>here</a> to sign up!</p>
        {:else}
            <p>Existing user? Please click <a class="link" href={null} on:click={() => behavior = AuthBehavior.Login}>here</a> to log in!</p>
        {/if}
    </div>
</InfoBox>