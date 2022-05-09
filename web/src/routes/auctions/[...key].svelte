<script context="module">
    export async function load({ params }) {
        const { key } = params
        return { props: { auctionKey: key } }
    }
</script>

<script lang="ts">
    import Auction from "../../Auction.svelte";
    import Auctions from "../../Auctions.svelte";

    export let auctionKey;
</script>

{#if auctionKey === ""}
    <Auctions />
{:else}
    <Auction auctionKey={auctionKey} />
{/if}