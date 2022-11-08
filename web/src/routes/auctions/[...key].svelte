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
                    itemKey: key,
                    serverLoadedItem: auction.auction
                }
            }
        }
        return {
            status: response.status,
            error: new Error("Could not fetch auction on the server")
        }
    }
</script>

<script lang="ts">
    import { goto } from "$app/navigation";
    import ItemView from "$lib/components/ItemView.svelte";
    import { fromJson } from "$lib/types/auction";
    import { onMount } from "svelte";

    export let itemKey;
    export let serverLoadedItem;

    onMount(async () => {
        if (itemKey === "" || itemKey === null) {
            goto('/');
        }
    });
</script>

{#if itemKey !== ""}
    <ItemView
        {itemKey}
        loader={{ endpoint: 'auctions', responseField: 'auction', fromJson }}
        serverLoadedItem={fromJson(serverLoadedItem)}
    />
{/if}
