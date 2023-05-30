<script lang="ts">
    import { onMount } from 'svelte';
    import { NostrPublicKey } from "$lib/stores";
    import {requestLoginModal} from "$lib/utils";
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import Minus from "$sharedLib/components/icons/Minus.svelte";

    let isSuperAdmin: boolean = false;

    onMount(async () => {
        let response = await fetch('config.json')
        let config = await response.json();
        if ($NostrPublicKey === config.admin_pubkey) {
            isSuperAdmin = true;
        }
    });
</script>

<div class="w-full items-center justify-center text-center">
    {#if $NostrPublicKey}
        {#if isSuperAdmin}
            <p>To add stalls to the homepage default view, go to the <a class="btn btn-sm btn-primary btn-outline" href="/stalls">Stall Browser</a>
                and add them or remove them using the <span class="inline-block text-green-500 align-middle"><Plus /></span> and
                <span class="inline-block text-rose-500 align-middle"><Minus /></span> icons at the right.</p>
        {:else}
            <p>You need to be the owner of this website to be able to customize its default appearance.</p>
            <p class="mt-6">To claim ownership, you need to edit the file <code>config.json</code> and put there your Nostr public key. You'll then be able to come to this page and learn how to do it.</p>
        {/if}
    {:else}
        <p>You need to be the owner of this website and login using your Nostr account:</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    {/if}
</div>
