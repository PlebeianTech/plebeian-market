<svelte:head>
    <title>Stores</title>
</svelte:head>

<script context="module">
    export async function load({ params }) {
        const { slug } = params;
        return { props: { storeName: slug } }
    }
</script>

<script lang="ts">
    import StoreView from "$lib/components/StoreView.svelte";
    export let storeName: string;
</script>


<StoreView  storeName={storeName}/>
