<script context="module">
    import { getBaseApiUrl } from "$lib/utils";

    export async function load({ params, fetch }) {
        const { key } = params;
        const auctionUrl = `${getBaseApiUrl()}/api/auctions/${key}`;
        const response = await fetch(auctionUrl)
        const auction = await response.json()
        if (response.ok) {
            return {
                props: {
                    auctionKey: key,
                    metaAuction: auction.auction
                }
            }
        }
        return {
            status: response.status,
            error: new Error("Could not fetch auction")
        }
    }
</script>

<script lang="ts">
    import { goto } from "$app/navigation";
    import AuctionView from "$lib/components/AuctionView.svelte"
    import { onMount } from "svelte";
    import { fromJson } from "$lib/types/auction";
    export let auctionKey;
    export let metaAuction;

    onMount(async () => {
        if (auctionKey === "" || auctionKey === null) {
            goto('/stall');
        }
    });
</script>

{#if auctionKey !== ""}
    <AuctionView auctionKey={auctionKey} metaAuction={fromJson(metaAuction)}/>
{/if}
