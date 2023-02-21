<script lang="ts">
    import {user} from "$lib/stores";
    import {getPublicKey} from "nostr-tools";
    import {onMount} from "svelte";
    import {hasExtension} from "$lib/nostr/utils";

    let nostr_public_key = getPublicKey($user.nostr_private_key);
    let nostrExtensionEnabled: boolean;

    onMount(async () => {
        nostrExtensionEnabled = hasExtension();
    })
</script>

<div class="text-2xl breadcrumbs">
    <ul>
        <li>Settings</li>
        <li>Nostr</li>
    </ul>
</div>

<div class="mt-8">
    {#if !nostrExtensionEnabled}
        <div class="alert alert-success shadow-lg">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <span>We have detected that you have a Nostr extension in your browser, so you'll be able to use your
                own identity in the entire Plebeian Market.</span>
            </div>
        </div>

    {:else}
        <div class="alert alert-warning shadow-lg">
            <div>
                <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                <span>You don't have a Nostr extension</span>
            </div>
        </div>

        <div class="mt-4 text-justify">
            <p>You're using your Plebeian Market generated Nostr identity. We created this for you as we detected
                that you're not using a Nostr browser extension. This is not a problem and you can continue using
                Plebeian Market this way, but it's highly recommended that you install a Nostr browser extension
                and create your own Nostr identity so nobody knows your private key.</p>

            <p class="mt-3 text-justify">You can use any of this browser extensions:
                <a class="link" href="https://getalby.com/" target="_blank" rel="noreferrer">Alby</a>,
                <a class="link" href="https://github.com/fiatjaf/nos2x" target="_blank" rel="noreferrer">nos2x</a> or
                <a class="link" href="https://www.blockcore.net/wallet" target="_blank" rel="noreferrer">Blockcore</a>.
            </p>

            <p class="mt-3 text-justify">In the meantime, this is your Nostr public key:</p>
        </div>

        <div class="w-full flex items-center justify-center mt-4">
            <div class="form-control w-full">
                <input bind:value={nostr_public_key} type="text" id="nostr_public_key" name="nostr_public_key" class="input input-lg input-bordered" />
            </div>
        </div>
    {/if}
</div>

<div class="mt-8">
    <p>Plebeian Market uses <b>Nostr</b> to support the following functionalities:</p>
    <ul class="list-disc list-inside">
        <li class="mt-3">Powering the Market Square and the Stall chat</li>
    </ul>

    <p class="mt-10">Features <i>coming soon</i>:</p>
    <ul class="list-disc list-inside">
        <li class="mt-3">Login with Nostr</li>
        <li>Publish your Resumé to Nostr</li>
        <li>Publish your Products to Nostr</li>
        <li>Publish your Auctions to Nostr</li>
        <li>Private decentralized communications between market members</li>
        <li>Synchronize with other stores through Nostr</li>
    </ul>
</div>
