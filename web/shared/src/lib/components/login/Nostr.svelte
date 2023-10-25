<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import {NostrPrivateKey, NostrPublicKey} from "$sharedLib/stores";
    import { hasExtension, tryLoginToBackend } from '$sharedLib/nostr/utils';
    import {generatePrivateKey, getPublicKey} from "nostr-tools";
    import { browser } from "$app/environment";
    import AlertInfo from "$sharedLib/components/icons/AlertInfo.svelte";
    import {setLoginMethod} from "$sharedLib/utils";
    import PrivateKeyInfo from "$sharedLib/components/PrivateKeyInfo.svelte";

    const dispatch = createEventDispatcher();

    let activeTab: number = 0;
    let newPrivateKey: string | null = null;
    let showPrivateKeyInfo: boolean = false;

    $: if ($NostrPublicKey) {
        // If login was called because $NostrPublicKey was not available
        // but immediately after it became available, dispatch a login
        // event so the dialog is closed asap
        dispatch('login', {});
    }

    async function getKeyFromExtension() {
        let publicKey = await (window as any).nostr.getPublicKey();

        setLoginMethod('extension');

        localStorage.setItem('nostrPublicKey', publicKey);
        NostrPublicKey.set(publicKey);

        await waitAndLogin();
        closeLoginModal();
    }

    async function useSameKeyToLogin() {
        setLoginMethod('generated');
        await savePrivateNostrKey($NostrPrivateKey);

        showPrivateKeyInfo = true;
    }

    async function generateNewNostrKey() {
        let privateKey = generatePrivateKey();
        setLoginMethod('generated');
        await savePrivateNostrKey(privateKey);

        showPrivateKeyInfo = true;
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

        NostrPrivateKey.set(privateKey);
        NostrPublicKey.set(publicKey);

        await waitAndLogin();
    }

    async function waitAndLogin() {
        await new Promise(resolve => setTimeout(resolve, 1000));
        dispatch('login', {});

        // After login, try to log in to backend
        tryLoginToBackend(() => { dispatch('backoffice-login') });
    }

    function closeLoginModal() {
        dispatch('close', {});
    }

    onMount(async () => {
        if (browser && !hasExtension()) {
            activeTab = 1;
        }

        /*
        if ($NostrPrivateKey && !$NostrPublicKey) {
            console.log('Nostr Public Key not available (because logged-out previously?) but Private Key present. Logging in...');
            await savePrivateNostrKey($NostrPrivateKey);
        }
        */
    });
</script>

{#if !showPrivateKeyInfo}
    {#if browser && !hasExtension()}
        <div class="alert alert-info mt-3 mb-12 flex justify-center items-center">
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
    {/if}

    <div>
        <div class="tabs">
            <a class="tab tab-lifted tab-sm md:tab-lg flex-1 p-4 pb-8 lg:pb-6 lg:py-2 {activeTab===0 ? 'bg-base-300 text-base-content' : ''}" on:click={() => activeTab=0}>Existing Nostr user</a>
            <a class="tab tab-lifted tab-sm md:tab-lg flex-1 p-4 pb-8 lg:pb-6 lg:py-2 {activeTab===1 ? 'bg-base-300 text-base-content' : ''}" on:click={() => activeTab=1}>New user / Anon</a>
        </div>

        <div class="grid w-full flex-grow gap-3 p-4 py-6 lg:p-14 lg:py-8 bg-base-300 rounded-xl rounded-tl-none rounded-tr-none md:shadow-xl items-center justify-center">
            {#if activeTab===0}
                {#if hasExtension}
                    <div class="flex mt-6 items-center justify-center text-warning">
                        Recommended
                    </div>
                    <div class="flex w-full items-center justify-center">
                        <button class="btn btn-success" on:click={getKeyFromExtension}>Use Nostr browser extension</button>
                    </div>

                    <div class="divider py-6 md:py-8">OR</div>
                {/if}

                <div class="w-full flex items-center justify-center">
                    <div class="form-control w-full max-w-full">
                        <input class="input md:input-md input-bordered" bind:value={newPrivateKey} type="text" placeholder="Paste your Nostr private key" />
                        <p class="mt-4 mb-2 text-xs">It will be stored in the web browser of this device, so Plebeian Market will have no way to access it.</p>
                    </div>
                </div>

                <div class="w-full flex items-center justify-center">
                    <button class="btn btn-primary" on:click={saveProvidedNostrKey}>Save the private key</button>
                </div>

            {:else if activeTab===1}
                <div class="w-full flex pt-16">
                    <div class="form-control w-full max-w-full">
                        <p class="mb-4">
                            This is the way to start using Plebeian Market if you don't have a Nostr extension or you want to have an anonymous identity.
                            <button class="btn btn-outline btn-xs btn-info" on:click={() => {window.modal_generate_key.showModal()}}>More info</button>
                        </p>


                        {#if $NostrPrivateKey}
                            <div class="form-control w-full max-w-full mt-8">
                                <p class="mb-4">This is the key we previously generated for you. You can use it or generate a new one.</p>
                                <p class="mb-4"><b>If you generate a new one, you'll better make sure you save this one to a secure place before, or you'll lose your ability to communicate with sellers and keep the Orders history.</b></p>
                                <input bind:value={$NostrPrivateKey} type="text" class="input md:input-lg input-bordered" />
                            </div>
                        {/if}
                    </div>
                </div>

                <div class="w-full flex items-center justify-center mt-8 mb-12">
                    {#if $NostrPrivateKey}
                        <button class="btn btn-success btn-xs md:btn-md mr-8" on:click={useSameKeyToLogin}>Use this key</button>
                    {/if}
                    <button class="btn btn-primary btn-xs md:btn-md" on:click={generateNewNostrKey}>Generate a new Nostr key</button>
                </div>
            {/if}
        </div>
    </div>
{:else}
    <PrivateKeyInfo showActionButtons={false} />

    <div class="flex justify-center items-center">
        <button id="close-window" class="btn btn-success btn-sm md:btn-md" on:click|preventDefault={closeLoginModal}>I understand, close this</button>
    </div>
{/if}

<dialog id="modal_generate_key" class="modal">
    <form method="dialog" class="modal-box">
        <p class="mt-4">With this option you can let us <b>generate a new Nostr private key</b> for you. In this way you are also essentially <b>buying products anonymously</b>, because the freshly generated key is not associated with any other identities you may be already using on Nostr.</p>
        <p class="mt-4">This is the recommended option if you don't have a Nostr extension or a Nostr identity already created.</p>
        <p class="mt-4">A new Nostr private key will be <b>generated and stored in the web browser of this device</b>, so no other person will have access to it.</p>
        <div class="modal-action">
            <button on:click={window.modal_generate_key.close()} class="btn">Close</button>
        </div>
    </form>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
