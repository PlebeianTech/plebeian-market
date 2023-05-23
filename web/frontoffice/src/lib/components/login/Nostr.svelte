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
//            await savePrivateNostrKey($NostrPrivateKey);
        }

        // if (!$NostrPrivateKey && !$NostrPublicKey && window && window.nostr) {
        //    await getKeyFromExtension()
        // }
    });
</script>

{#if browser && hasExtension()}
    <div class="py-20">
        <div class="w-full flex items-center justify-center">
            <div class="form-control w-full max-w-full">
                <p>A Nostr extension is the most secure and recommended way to use Plebeian Market.</p>
                <label class="label mt-8" for="npub">
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
    <div class="alert alert-info bg-blue-400/70 shadow-lg my-3 flex justify-center items-center">
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
                <p>You need a Nostr key to be able to buy products in Plebeian Market. You can let us generate one for you, or you can provide one if you have one.</p>
            </span>
        </div>
    </div>

    <div>
        <div class="tabs">
            <a class="tab tab-lifted tab-lg flex-1" class:tab-active={activeTab===0} on:click={() => activeTab=0}>Generate New Nostr Key</a>
            <a class="tab tab-lifted tab-lg flex-1" class:tab-active={activeTab===1} on:click={() => activeTab=1}>Provide own Private Key</a>
        </div>

        <div class="bg-blue-700/20 grid w-full flex-grow gap-3 rounded-xl rounded-tl-none rounded-tr-none p-6 shadow-xl">
            {#if activeTab===0}
                <div class="w-full flex items-center justify-center p-8">
                    {#if $NostrPrivateKey}
                        <div class="form-control w-full max-w-full">
                            <label class="label" for="npub">
                                <span class="label-text">Your NPUB</span>
                            </label>
                            <input bind:value={$NostrPrivateKey} type="text" class="input input-lg input-bordered" />
                        </div>
                    {:else}
                        <p>A new Nostr private key will be generated and stored in this web browser, so no other person will have access to it.</p>
                    {/if}
                </div>

                <div class="w-full flex items-center justify-center gap-5">
                    <button class="btn btn-primary" on:click={generateNewNostrKey}>Generate new Nostr key</button>
                </div>

            {:else if activeTab===1}
                <div class="w-full flex items-center justify-center p-8">
                    <div class="form-control w-full max-w-full">
                        <p>Introduce your Nostr private key. It will be stored in this web browser, so no other person will have access to it.</p>
                        <input bind:value={newPrivateKey} type="text" class="input input-lg input-bordered mt-6" />
                    </div>
                </div>

                <div class="w-full flex items-center justify-center gap-5">
                    <button class="btn btn-primary" on:click={saveProvidedNostrKey}>Save the private key</button>
                </div>
            {/if}
        </div>
    </div>
{/if}
