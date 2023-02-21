<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import LnurlLogin from "$lib/components/login/Lnurl.svelte";
    import NostrLogin from "$lib/components/login/Nostr.svelte";
    import { isProduction } from "$lib/utils";

    const dispatch = createEventDispatcher();

    export let onLogin = () => {};

    enum LoginType {
        Lnurl,
        Nostr,
    }

    let type = LoginType.Lnurl;

    onMount(() => { type = LoginType.Lnurl });
</script>

<div class="w-full flex items-center justify-center mt-4">
    <div class="tabs tabs-boxed">
        <a class="tab tab-lg" class:tab-active={type === LoginType.Lnurl} href={null} on:click={() => type = LoginType.Lnurl}>LNURL</a>
        {#if !isProduction()}
            <a class="tab tab-lg" class:tab-active={type === LoginType.Nostr} href={null} on:click={() => type = LoginType.Nostr}>Nostr</a>
        {/if}
    </div>
</div>

{#if type === LoginType.Lnurl}
    <LnurlLogin {onLogin} on:login={(_) => dispatch('login', {})} />
{:else if type === LoginType.Nostr}
    <NostrLogin {onLogin} on:login={(_) => dispatch('login', {})} />
{/if}