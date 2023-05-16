<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import type { User } from "$lib/types/user";
    import { NostrPublicKey } from "$lib/stores";
    import { hasExtension, encodeNpub } from '$lib/nostr/utils';

    const dispatch = createEventDispatcher();

    export let onLogin: (user: User | null) => void = (_) => {};

    let npub: string | null = null;

    async function getKeyFromExtension() {
        let pubKey = await (window as any).nostr.getPublicKey();

        npub = encodeNpub(pubKey);
        localStorage.setItem('nostrPublicKey', pubKey);
        $NostrPublicKey = pubKey;

        await new Promise(resolve => setTimeout(resolve, 1000));
        dispatch('login', {});
    }
</script>

{#if hasExtension()}
    <div class="py-24">
        <div class="w-full flex items-center justify-center">
            <div class="form-control w-full max-w-full">
                <label class="label" for="npub">
                    <span class="label-text">Your NPUB</span>
                </label>
                <input bind:value={npub} type="text" id="npub" name="npub" class="input input-lg input-bordered" />
            </div>
        </div>
        <div class="w-full flex items-center justify-center mt-8 gap-5">
            <button class="btn btn-primary" on:click={getKeyFromExtension}>Get from extension and login</button>
        </div>
    </div>
{:else}
    <div class="alert alert-warning shadow-lg my-24 flex justify-center items-center">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span>
                <p>You need a Nostr extension to be able to <b>Login</b> into Plebeian Market.</p>
                <p>You can browse stalls and products without the extension, but you will <b>need one</b> if you want to <b>buy products</b>.</p>
            </span>
        </div>
    </div>
{/if}
