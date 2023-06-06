<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import type { User } from "$lib/types/user";
    import {NostrPrivateKey, NostrPublicKey} from "$lib/stores";
    import { hasExtension, encodeNpub } from '$lib/nostr/utils';
    import {generatePrivateKey, getPublicKey} from "nostr-tools";
    import { browser } from "$app/environment";

    const dispatch = createEventDispatcher();

    export let onLogin: (user: User | null) => void = (_) => {};

    let npub: string | null = null;
    let activeTab: number = 0;
    let newPrivateKey: string | null = null;

    $: if ($NostrPublicKey) {
        // If login was called because $NostrPublicKey was not available
        // but immediately after it became available, dispatch a login
        // event so the dialog is closed
        waitAndlogin();
    }

    async function getKeyFromExtension() {
        let publicKey = await (window as any).nostr.getPublicKey();

        npub = encodeNpub(publicKey);
        localStorage.setItem('nostrPublicKey', publicKey);
        $NostrPublicKey = publicKey;

        await waitAndlogin();
    }

    async function generateNewNostrKey() {
        let privateKey = generatePrivateKey();
        await savePrivateNostrKey(privateKey);
    }

    async function saveProvidedNostrKey() {
        await savePrivateNostrKey(newPrivateKey);
    }

    async function savePrivateNostrKey(privateKey) {
        let publicKey = getPublicKey(privateKey);

        localStorage.setItem('nostrPrivateKey', privateKey);
        localStorage.setItem('nostrPublicKey', publicKey);

        $NostrPrivateKey = privateKey;
        $NostrPublicKey = publicKey;

        await waitAndlogin();
    }

    async function waitAndlogin() {
        await new Promise(resolve => setTimeout(resolve, 1000));
        dispatch('login', {});
    }

    onMount(async () => {
        if ($NostrPrivateKey && !$NostrPublicKey) {
            console.log('Nostr Public Key not available (because logged-out previously?) but Private Key present. Logging in...');
            // await savePrivateNostrKey($NostrPrivateKey);
        }
    });
</script>

{#if browser && hasExtension()}
    <div class="py-20">
        <div class="w-full flex items-center justify-center">
            <div class="form-control w-full max-w-full">
                <p>A Nostr extension is the most secure and recommended way to use Plebeian Market.</p>
                {#if npub}
                    <label class="label mt-8" for="npub">
                        <span class="label-text">Your NPUB</span>
                    </label>

                    <input bind:value={npub} type="text" id="npub" name="npub" class="input md:input-lg input-bordered" />
                {/if}
            </div>
        </div>
        <div class="w-full flex items-center justify-center mt-8 gap-5">
            <button class="btn btn-primary" on:click={getKeyFromExtension}>Use Nostr browser extension</button>
        </div>
    </div>
{:else}
    <div class="alert alert-info mt-3 mb-6 flex justify-center items-center">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <!-- Desktop -->
            <span class="hidden md:block">
                <p>It's recommended that you use a Nostr browser extension in your browser to be able to buy products in Plebeian Market.</p>
                <p class="mt-2">
                    You can try <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a>,
                    <a class="link" href="https://chrome.google.com/webstore/detail/nos2x/kpgefcfmnafjgpblomihpgmejjdanjjp" target="_blank" rel="noreferrer">nos2x</a> or
                    <a class="link" href="https://kollider.xyz/wallet" target="_blank" rel="noreferrer">Kollider</a> and
                    load this screen again, or use one of this alternatives:
                </p>
            </span>
            <!-- Mobile -->
            <span class="md:hidden">
                <p>You need a <b>Nostr private key</b> to be able to buy products in Plebeian Market. You can let us generate one for you, or you can provide one if you have one.</p>
            </span>
        </div>
    </div>

    <div>
        <div class="tabs">
            <a class="tab tab-lifted tab-sm md:tab-lg flex-1 py-2 {activeTab===0 ? 'bg-base-300 text-base-content' : ''}" on:click={() => activeTab=0}>Generate New Key</a>
            <a class="tab tab-lifted tab-sm md:tab-lg flex-1 py-2 {activeTab===1 ? 'bg-base-300 text-base-content' : ''}" on:click={() => activeTab=1}>Introduce Key</a>
        </div>

        <div class="grid w-full flex-grow gap-3 p-6 bg-base-300 rounded-xl rounded-tl-none rounded-tr-none md:shadow-xl">
            {#if activeTab===0}
                <div class="w-full flex items-center justify-center">
                    {#if $NostrPrivateKey}
                        <div class="form-control w-full max-w-full">
                            <p class="mb-4 md:mb-6">Your Nostr private key</p>
                            <input bind:value={$NostrPrivateKey} type="text" class="input md:input-lg input-bordered" />
                        </div>
                    {:else}
                        <p>A new Nostr private key will be generated and stored in this web browser, so no other person will have access to it.</p>
                    {/if}
                </div>

                <div class="w-full flex items-center justify-center mt-3">
                    <button class="btn btn-primary" on:click={generateNewNostrKey}>Generate new Nostr key</button>
                </div>

            {:else if activeTab===1}
                <div class="w-full flex items-center justify-center">
                    <div class="form-control w-full max-w-full">
                        <p class="mb-4 md:mb-6">Introduce your Nostr private key. It will be stored in this web browser, so no other person will have access to it.</p>
                        <input bind:value={newPrivateKey} type="text" class="input md:input-lg input-bordered" />
                    </div>
                </div>

                <div class="w-full flex items-center justify-center mt-3">
                    <button class="btn btn-primary" on:click={saveProvidedNostrKey}>Save the private key</button>
                </div>
            {/if}
        </div>
    </div>
{/if}
