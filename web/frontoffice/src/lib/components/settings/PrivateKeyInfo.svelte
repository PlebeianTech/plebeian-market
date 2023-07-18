<script>
    import {NostrPrivateKey} from "$sharedLib/stores";
    import {logout} from "$sharedLib/utils.js";

    function deletePrivateKey() {
        localStorage.removeItem('nostrPrivateKey');
        NostrPrivateKey.set(null);

        logout();
    }
</script>

<p class="text-xl">Your Nostr private key:</p>

<pre class="my-8 text-lg bg-base-300 text-center">{$NostrPrivateKey}</pre>

<p>
    Please, don't share this key with anyone. This key represents your Nostr private identity, so the products you buy and the messages you send are associated with it.
    The key is stored in your web browser, so Plebeian Market has no way to know it.
</p>
<p class="mt-4">
    You should backup this key if you want to use it in other clients or in case it's deleted from your browser.
</p>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="delete-private-key" class="btn btn-primary" on:click|preventDefault={deletePrivateKey}>Delete Private Key</button>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save-profile" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={save}>Save</button>
</div>
