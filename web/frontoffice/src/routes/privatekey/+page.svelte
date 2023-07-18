<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {NostrPrivateKey, NostrLoginMethod} from "$sharedLib/stores";
    import PrivateKeyInfo from "$lib/components/settings/PrivateKeyInfo.svelte";
    import {loggedIn, logout, requestLoginModal} from "$sharedLib/utils";
</script>

<svelte:head>
    <title>Private Key Management</title>
</svelte:head>

<Titleh1>Private Key Management</Titleh1>

{#if loggedIn()}
    {#if $NostrLoginMethod === 'extension'}
        <div class="w-full items-center justify-center text-center">
            <p>You're using your Nostr browser extension, so you don't need to manage your Private key.</p>
            <button class="btn btn-info mt-4" on:click={() => logout()} on:keypress={() => logout()}>Logout</button>
        </div>
    {:else}
        {#if $NostrPrivateKey}
            <PrivateKeyInfo />
        {:else}
            <div class="w-full items-center justify-center text-center">
                <p>We don't have a Private Key stored in the browser yet. You need to login first:</p>
                <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
            </div>
        {/if}
    {/if}
{:else}
    <div class="w-full items-center justify-center text-center">
        <p>You still have to login to Plebeian Market.</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    </div>
{/if}
