<svelte:head>
    <title>Market Stall</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { stallOwnerNym: slug } }
    }
</script>

<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import StallView from "$lib/components/StallView.svelte";

    export let stallOwnerNym: string;

    onMount(async () => {
        if (stallOwnerNym === "" || stallOwnerNym === null) {
            goto('/');
        }
    });
</script>

<StallView stallOwnerNym={stallOwnerNym} />
