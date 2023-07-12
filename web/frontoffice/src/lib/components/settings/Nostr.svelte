<script lang="ts">
    import {NostrPrivateKey, NostrPublicKey} from "$sharedLib/stores";
    import {logout, requestLoginModal} from "$sharedLib/utils";
    import {hasExtension} from "$sharedLib/nostr/utils";

    function deletePrivateKey() {
        localStorage.removeItem('nostrPrivateKey');
        NostrPrivateKey.set(null);

        logout();
    }
</script>

{#if $NostrPublicKey}
    {#if hasExtension()}
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
        <p class="text-xl">Your Nostr private key:</p>

        <pre class="my-8 text-lg bg-base-300 text-center">{$NostrPrivateKey}</pre>

        <p>
            Please, don't share this key with anyone. This key represents your Nostr private identity, so the products you buy and the messages you send are associated with it.
            The key is stored in your web browser, so Plebeian Market has no way to know it.
        </p>
        <p class="mt-4">
            You should backup this key if you want to use it in other clients or in case it's deleted from your browser.
        </p>

        <!--
        <div class="flex justify-center items-center mt-4 h-15">
            <button id="save-profile" class="btn btn-primary" on:click|preventDefault={deletePrivateKey}>Delete Private Key</button>
        </div>
        -->

        <!--
        <div class="flex justify-center items-center mt-4 h-15">
            <button id="save-profile" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={save}>Save</button>
        </div>
        -->
    {/if}

    <button class="btn btn-info mt-4" on:click={() => logout()} on:keypress={() => logout()}>Logout</button>

{:else}
    <div class="w-full items-center justify-center text-center">
        <p>You still have to login to Plebeian Market.</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    </div>
{/if}
