<script>
    import {NostrLoginMethod, NostrPrivateKey} from "$sharedLib/stores";
    import {logout} from "$sharedLib/utils";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";

    function deletePrivateKey() {
        localStorage.removeItem('nostrPrivateKey');
        NostrPrivateKey.set(null);

        logout();
    }
</script>

<InfoBox classText="mb-8 md:mb-12">
    {#if $NostrLoginMethod === 'generated'}
        <p>This is the <b>Private Nostr key</b> that <b>we generated for you</b>. It's used for:</p>
    {:else if $NostrLoginMethod === ''}
        <p>This is the <b>Private Nostr key</b> that <b>you provided</b>. It's used for:</p>
    {:else}
        <p>This is the <b>Private Nostr key</b>. It's used for:</p>
    {/if}

    <ul class="my-4 ml-6">
        <li>- Buy products</li>
        <li>- Participate in auctions</li>
        <li>- See the status of your orders</li>
        <li>- Contact with merchants</li>
        <li>- Build your reputation</li>
        <li>- And more</li>
    </ul>
    <p><b>You should backup the key in a safe place</b>, because it's stored in your browser and it can be lost after an operative system or browser update.</p>

    <p class="mt-4">
        Please, <b>don't share this key with anyone</b>. This key represents your Nostr private identity. The key is stored in your web browser, so Plebeian Market has no way to know it.
    </p>
</InfoBox>

<p class="text-xl">Your Nostr private key:</p>

<pre class="my-8 text-lg bg-base-300 text-center">{$NostrPrivateKey}</pre>

<div class="w-full flex items-center justify-center mt-8 h-15">
    <div class="flex justify-center items-center mr-8">
        <button id="delete-private-key" class="btn btn-error" on:click|preventDefault={deletePrivateKey}>Delete Private Key</button>
    </div>

    <div class="flex justify-center items-center">
        <button id="save-profile" class="btn btn-warning" on:click|preventDefault={() => {logout()}}>Logout</button>
    </div>
</div>
