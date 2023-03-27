<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { ErrorHandler, loginNostr } from "$lib/services/api";
    import type { User } from "$lib/types/user";
    import { Info, Error, nostrUser } from "$lib/stores";
    import { hasExtension } from '$lib/nostr/utils';
    import {getPublicKey, nip19} from "nostr-tools";

    const dispatch = createEventDispatcher();

    export let onLogin: (user: User | null) => void = (_) => {};

    let npub: string | null = null;
    let privKeyInput: string | null = null;
    let privateKeyLoginMode = false;

    async function getKeyFromExtension() {
        let pubkey = await window.nostr.getPublicKey();

        await new Promise(resolve => setTimeout(resolve, 2000));

        nostrUser.set({
            privateKey: null,
            publicKey: pubkey,
        });

        localStorage.setItem('nostrPublicKey', pubkey);

        loginActions();
    }

    function savePrivateKey() {
        let privKey;

        // console.log('length', privKeyInput.length);
        if (!privKeyInput) {
            Error.set("You have to introduce your Nostr private key.");
            return;
        }
        if (privKeyInput.startsWith('npub')) {
            Error.set("You have introduced a public key, but a private key starting with 'nsec' is required.");
            return;
        }
        if (![63, 64].includes(privKeyInput.length)) {
            Error.set("A Nostr private key must be 63/64 characters long. The one you introduced has: " + privKeyInput.length);
            return;
        }

        if (privKeyInput.startsWith('nsec')) {
            console.log('savePrivateKey - nsec detected. Decoding...');
            let {type, data} = nip19.decode(privKeyInput);
            console.log('savePrivateKey - Decoded');
            privKey = data;
        } else {
            privKey = privKeyInput;
        }

        // console.log('savePrivateKey - PrivKey: ' + privKey);

        let pubKey = getPublicKey(privKey);
        // console.log('savePrivateKey - PubKey: ' + pubKey);

        nostrUser.set({
            privateKey: privKey,
            publicKey: pubKey,
        });

        localStorage.setItem('nostrPrivateKey', privKey);

        loginActions();
    }

    function loginActions() {
        Info.set("¡Hello, you're so early!");
        dispatch('login', {});
    }

    onMount(() => {
        if (! hasExtension()) {
            privateKeyLoginMode = true;
        }
    });
</script>

<div class="py-16 flex justify-center items-center">
    <div>
        {#if npub}
            <div class="w-full flex items-center justify-center mt-4">
                <div class="form-control w-full max-w-full">
                    <label class="label" for="npub">
                        <span class="label-text">Login with your NPUB:</span>
                    </label>
                    <input bind:value={npub} type="text" name="npub" id="npub" class="input input-lg input-bordered" />
                </div>
            </div>
        {/if}

        {#if !npub && !privateKeyLoginMode}
            <div class="w-full flex items-center justify-center mt-4 gap-5">
                <button class="btn btn-primary" class:btn-disabled={!hasExtension} on:click={getKeyFromExtension}>Login using extension</button>
                <button class="btn btn-primary" on:click={() => privateKeyLoginMode = true}>Provide private key</button>
            </div>
            <div class="w-full flex items-center justify-center mt-4">
                {#if hasExtension()}
                    You have a Nostr browser extension, so we highly recommend login that way.
                {:else}
                    <!-- Mobile -->
                    <div class="lg:hidden">You can provide your Nostr private key. It will be stored locally on your device and it will never be transmitted to our servers.</div>
                    <!-- Desktop -->
                    <div class="hidden lg:block">You don't have a Nostr browser extension enabled - It's highly advised to use a browser extension (<a class="link" href="/faq" target="_blank">see why</a>).</div>
                {/if}
            </div>
        {/if}

        {#if privateKeyLoginMode}
            <div class="w-full flex items-center justify-center mt-4">
                <div class="form-control w-full max-w-full">
                    <label class="label" for="privateKeyInput">
                        <span class="label-text">Nostr private key</span>
                    </label>
                    <input bind:value={privKeyInput} type="text" name="privateKeyInput" id="privateKeyInput" class="input input-lg input-bordered" />
                </div>
            </div>
            <div class="w-full flex items-center justify-center mt-4 gap-5">
                <button class="btn btn-secondary" on:click={savePrivateKey}>Save</button>
                <button class="btn btn-secondary" on:click={() => privateKeyLoginMode = false}>Back</button>
            </div>
        {/if}
    </div>
</div>
