<script lang="ts">
    import { goto } from "$app/navigation";
    import ItemView from "$lib/components/ItemView.svelte"
    import { fromJson } from "$lib/types/auction";
    import { onMount } from "svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    onMount(async () => {
        if (data.itemKey === "" || data.itemKey === null) {
            goto('/');
        }
    });
</script>


{#if data.itemKey !== ""}
    <ItemView
            itemKey={data.itemKey}
            loader={{endpoint: 'auctions', responseField: 'auction', fromJson }}
            serverLoadedItem={fromJson(data.serverLoadedItem)}
    />
{/if}

