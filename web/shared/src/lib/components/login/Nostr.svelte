<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import {NostrPrivateKey, NostrPublicKey} from "$sharedLib/stores";
    import { hasExtension, encodeNpub, tryLoginToBackend } from '$sharedLib/nostr/utils';
    import {generatePrivateKey, getPublicKey} from "nostr-tools";
    import { browser } from "$app/environment";
    import AlertInfo from "$sharedLib/components/icons/AlertInfo.svelte";
    import {setLoginMethod} from "$sharedLib/utils";

    const dispatch = createEventDispatcher();

    // export const onLogin: () => void = () => {};

    let npub: string | null = null;
    let activeTab: number = 0;
    let newPrivateKey: string | null = null;

    $: if ($NostrPublicKey) {
        // If login was called because $NostrPublicKey was not available
        // but immediately after it became available, dispatch a login
        // event so the dialog is closed
        dispatch('login', {});
    }

    async function getKeyFromExtension() {
        let publicKey = await (window as any).nostr.getPublicKey();

        npub = encodeNpub(publicKey);

        setLoginMethod('extension');

        localStorage.setItem('nostrPublicKey', publicKey);
        $NostrPublicKey = publicKey;

        await waitAndlogin();
    }

    async function useSameKeyToLogin() {
        setLoginMethod('generated');
        await savePrivateNostrKey($NostrPrivateKey);
    }

    async function generateNewNostrKey() {
        let privateKey = generatePrivateKey();
        setLoginMethod('generated');
        await savePrivateNostrKey(privateKey);
    }

    async function saveProvidedNostrKey() {
        if (!newPrivateKey) {
            // TODO Alert telling the user to put the key in the field
            return;
        }

        setLoginMethod('provided');
        await savePrivateNostrKey(newPrivateKey);
    }

    async function savePrivateNostrKey(privateKey: string) {
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

        // After login, try to log in to backend
        tryLoginToBackend();
    }

    function activateFirstTabIfExtensionPresent() {
        if (browser && hasExtension())
            activeTab=0;
    }

    onMount(async () => {
        if (browser && !hasExtension()) {
            activeTab = 1;
        }

        if ($NostrPrivateKey && !$NostrPublicKey) {
            console.log('Nostr Public Key not available (because logged-out previously?) but Private Key present. Logging in...');
            // await savePrivateNostrKey($NostrPrivateKey);
        }
    });
</script>

{#if browser && !hasExtension()}
    <div class="alert alert-info mt-3 mb-12 flex justify-center items-center">
        <div>
            <AlertInfo />
            <!-- Desktop -->
            <span class="hidden md:block">
                <p>It's recommended that you use a Nostr browser extension in your browser to be able to buy products in Plebeian Market if you plan to build a reputation for your identity.</p>
                <p class="mt-2">
                    You can try <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a>,
                    <a class="link" href="https://chrome.google.com/webstore/detail/nos2x/kpgefcfmnafjgpblomihpgmejjdanjjp" target="_blank" rel="noreferrer">nos2x</a> or
                    <a class="link" href="https://kollider.xyz/wallet" target="_blank" rel="noreferrer">Kollider</a> and
                    reload this screen again, or use one of this alternatives:
                </p>
            </span>
            <!-- Mobile -->
            <span class="md:hidden">
                <p>You need a <b>Nostr private key</b> to be able to buy products in Plebeian Market. You can let us generate one for you, or you can provide one if you have one.</p>
            </span>
        </div>
    </div>
{/if}

<div>
    <div class="tabs">
        <a
           data-tip="You need a Nostr browser extension"
           class="indicator tab tab-lifted {browser && hasExtension() ? '' : 'tab-disabled tooltip tooltip-bottom tooltip-error'} tab-sm md:tab-lg flex-1 p-4 pb-8 lg:pb-6 lg:py-2 {activeTab===0 ? 'bg-base-300 text-base-content' : ''}" on:click={activateFirstTabIfExtensionPresent}>
            <span class="indicator-item indicator-center badge badge-md badge-error">recommended</span>
            Use Nostr extension
        </a>
        <a class="indicator tab tab-lifted tab-sm md:tab-lg flex-1 p-4 pb-8 lg:pb-6 lg:py-2 {activeTab===1 ? 'bg-base-300 text-base-content' : ''}" on:click={() => activeTab=1}>
            <span class="indicator-item indicator-center badge badge-md badge-warning">anonymous</span>
            Generate New Key
        </a>
        <a class="tab tab-lifted tab-sm md:tab-lg flex-1 p-4 pb-8 lg:pb-6 lg:py-2 {activeTab===2 ? 'bg-base-300 text-base-content' : ''}" on:click={() => activeTab=2}>Use your private key</a>
    </div>

    <div class="grid w-full flex-grow gap-3 p-4 py-6 lg:p-14 lg:py-8 bg-base-300 rounded-xl rounded-tl-none rounded-tr-none md:shadow-xl items-center justify-center">
        {#if activeTab===0}
            <div class="w-full flex">
                <div class="form-control w-full max-w-full">
                    <p>A Nostr extension is the <b>most secure</b> and <b>recommended</b> way to use Plebeian Market.</p>
                    <p class="mt-4">By using the identity that you created in your Nostr extension, you will be <b>building your reputation</b> each time you buy or sell any product and act as a good pleb by paying on time or shipping in good order.</p>
                    {#if npub}
                        <label class="label mt-8" for="npub">
                            <span class="label-text">Your NPUB</span>
                        </label>

                        <input bind:value={npub} type="text" id="npub" name="npub" class="input md:input-lg input-bordered" />
                    {/if}
                </div>
            </div>
            <div class="w-full flex items-center justify-center mt-8 gap-5">
                <button class="btn btn-success" on:click={getKeyFromExtension}>Use Nostr browser extension</button>
            </div>

        {:else if activeTab===1}
            <div class="w-full flex">
                <div class="form-control w-full max-w-full">
                    <p>With this option you can let us generate a new Nostr private key for you. In this way you are also essentially buying products anonymously because the freshly generated key is not associated with any other identities you may be already using on Nostr.</p>
                    <p class="mt-4">This is the recommended option if you don't have a Nostr extension or a Nostr identity already created.</p>

                    {#if $NostrPrivateKey}
                        <div class="form-control w-full max-w-full mt-8">
                            <p class="mb-4">This is the key we generated for you. You can use it or generate a new one.</p>
                            <p class="mb-4"><b>If you generate a new one, you'll better make sure you save this one to a secure place before, or you'll lose your ability to communicate with sellers and keep the Orders history.</b></p>
                            <input bind:value={$NostrPrivateKey} type="text" class="input md:input-lg input-bordered" />
                        </div>
                    {:else}
                        <p>A new Nostr private key will be generated and stored in the web browser of this device, so no other person will have access to it.</p>
                    {/if}
                </div>
            </div>

            <div class="w-full flex items-center justify-center mt-3">
                {#if $NostrPrivateKey}
                    <button class="btn btn-success mr-8" on:click={useSameKeyToLogin}>Use this key</button>
                {/if}
                <button class="btn btn-warning" on:click={generateNewNostrKey}>Generate a new Nostr key</button>
            </div>

        {:else if activeTab===2}
            <div class="w-full flex items-center justify-center">
                <div class="form-control w-full max-w-full">
                    <p class="mb-4 md:mb-6">Paste your Nostr private key. It will be stored in the web browser, on this device, so Plebeian Market will have no way to access it. The only thing we will access is the public key associated to this private key!</p>
                    <input bind:value={newPrivateKey} type="text" class="input md:input-lg input-bordered" />
                </div>
            </div>

            <div class="w-full flex items-center justify-center mt-3">
                <button class="btn btn-primary" on:click={saveProvidedNostrKey}>Save the private key</button>
            </div>
        {/if}
    </div>
</div>
