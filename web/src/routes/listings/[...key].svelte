<script context="module">
    export async function load({ params }) {
        const { key } = params;
        return { props: { itemKey: key } }
    }
</script>

<script lang="ts">
    import { goto } from "$app/navigation";
    import ItemView from "$lib/components/ItemView.svelte"
    import { fromJson } from "$lib/types/listing";
    import { onMount } from "svelte";

    export let itemKey;

    onMount(async () => {
        if (itemKey === "" || itemKey === null) {
            goto('/');
        }
    });
</script>

{#if itemKey !== ""}
    <ItemView {itemKey} loader={{endpoint: 'listings', responseField: 'listing', fromJson}} />
{/if}
