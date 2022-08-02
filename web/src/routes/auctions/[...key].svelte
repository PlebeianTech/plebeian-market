<script context="module">
    export async function load({ params }) {
        const { key } = params;
        return { props: { auctionKey: key } }
    }
</script>

<script lang="ts">
    import { goto } from "$app/navigation";
    import AuctionView from "$lib/components/AuctionView.svelte"
    import { onMount } from "svelte";

    export let auctionKey;

    onMount(async () => {
        if (auctionKey === "" || auctionKey === null) {
            goto('/stall');
        }
    });
</script>

{#if auctionKey !== ""}
    <AuctionView auctionKey={auctionKey} />
{/if}
