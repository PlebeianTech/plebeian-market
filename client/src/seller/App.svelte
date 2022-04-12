<script>
    import { token } from "../common.js";
    import Login from '../Login.svelte';
    import Auctions from './Auctions.svelte';

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
