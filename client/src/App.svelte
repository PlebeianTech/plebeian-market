<script>
    import { onDestroy } from 'svelte';
    import { token } from "./stores.js";
    import Auctions from './Auctions.svelte';
    import Login from './Login.svelte';

    let tokenValue;

	const unsubscribe = token.subscribe(value => { tokenValue = value; });
	onDestroy(unsubscribe);
</script>

{#if tokenValue }
    <Auctions />
{:else }
    <Login />
{/if}
