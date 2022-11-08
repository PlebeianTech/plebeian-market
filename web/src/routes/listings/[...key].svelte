<script context="module">
    import { getBaseApiUrl } from "$lib/utils";

    export async function load({ params, fetch }) {
        const { key } = params;
        const listingUrl = `${getBaseApiUrl()}/api/listings/${key}`;
        const response = await fetch(listingUrl)
        const listing = await response.json()
        if (response.ok) {
            return {
                props: {
                    itemKey: key,
                    serverLoadedItem: listing.listing
                }
            }
        }
        return {
            status: response.status,
            error: new Error("Could not fetch listing on the server")
        }
    }
</script>

<script lang="ts">
    import { goto } from "$app/navigation";
    import ItemView from "$lib/components/ItemView.svelte";
    import { fromJson } from "$lib/types/listing";
    import { onMount } from "svelte";

    export let itemKey;
    export let serverLoadedItem;

    onMount(async () => {
        if (itemKey === "" || itemKey === null) {
            goto("/");
        }
    });
</script>

{#if itemKey !== ""}
    <ItemView
        {itemKey}
        loader={{ endpoint: "listings", responseField: "listing", fromJson }}
        serverLoadedItem={fromJson(serverLoadedItem)}
    />
{/if}
