<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import LnurlAuth from "$lib/components/auth/Lnurl.svelte";

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

{#if provider === Provider.Lnurl}
    <LnurlAuth {behavior} {onLogin} on:login={(_) => dispatch('login', {})} />
{/if}
