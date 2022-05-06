<script context="module">
    export async function load({ params }) {
        const { key } = params
        return { props: { auctionKey: key } }
    }
</script>

<script>
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { intent, token } from "../../stores.js";
    import Auction from "../../Auction.svelte";
    import Auctions from "../../Auctions.svelte";

    export let auctionKey;

    onMount(async () => {
        if (!$intent) {
            intent.set(auctionKey === "" ? 'seller' : auctionKey);
        }
        if ($intent === 'seller' && !$token) {
            goto("/login");
        }
    });
</script>

{#if auctionKey === ""}
    <Auctions />
{:else}
    <Auction auctionKey={auctionKey} />
{/if}