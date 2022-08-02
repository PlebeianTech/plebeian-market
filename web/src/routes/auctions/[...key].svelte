<script context="module">
    export async function load({ params }) {
        const { key } = params;
        return { props: { auctionKey: key } }
    }
</script>

<script lang="ts">
    import AuctionView from "$lib/components/AuctionView.svelte"

    export let auctionKey;

</script>

{#if auctionKey !== ""}
    <AuctionView auctionKey={auctionKey} />
{/if}
