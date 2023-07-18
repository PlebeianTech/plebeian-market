<script lang="ts">
    import {NostrLoginMethod, NostrPrivateKey, NostrPublicKey} from "$sharedLib/stores";
    import {loggedIn, logout, requestLoginModal} from "$sharedLib/utils";
    import PrivateKeyInfo from "$lib/components/settings/PrivateKeyInfo.svelte";
</script>

{#if loggedIn()}
    {#if $NostrLoginMethod === 'extension'}
        <p>
            You're using your <b>Nostr browser extension</b>.
        </p>
        <p class="mt-4">
            This is the <b>recommended</b> and <b>most secure</b> way to use Plebeian Market.
        </p>
        <p class="mt-4">
            This is the public key we're getting from the browser extension:
        </p>
        <p class="mt-4 mb-4">
            {$NostrPublicKey}
        </p>
    {:else if $NostrPrivateKey}
        <PrivateKeyInfo />
    {/if}

    <button class="btn btn-info mt-4" on:click={() => logout()} on:keypress={() => logout()}>Logout</button>

{:else}
    <div class="w-full items-center justify-center text-center">
        <p>You still have to login to Plebeian Market.</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    </div>
{/if}
