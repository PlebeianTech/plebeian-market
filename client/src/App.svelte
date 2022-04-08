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
<div id="top-menu">
    <button class="btn-white" on:click|preventDefault={logout}>Log out</button>
</div>
    <Auctions />
{:else}
    <Login />
{/if}
