<script>
    import { token } from "./stores.js";
    import Auctions from './Auctions.svelte';
    import Login from './Login.svelte';

    $token = sessionStorage.getItem('token');

    function logout() {
        $token = null;
    }
</script>

{#if $token}
    <button on:click|preventDefault={logout}>Log out</button>
    <Auctions />
{:else}
    <Login />
{/if}
