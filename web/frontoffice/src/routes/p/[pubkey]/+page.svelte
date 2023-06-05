<script lang="ts">
    import ResumeView from "$lib/components/resume/View.svelte";
    import StallsBrowser from "$lib/components/stores/Browse.svelte";

    /** @type {import('./$types').PageData} */
    export let data;
</script>

<div class="py-3 lg:pb-14 mx-auto w-screen lg:w-2/3">
    <StallsBrowser merchantPubkey={data.pubkey}></StallsBrowser>
</div>

<div class="py-3 lg:pb-14 mx-auto w-screen lg:w-2/3">
    <ResumeView pubkey={data.pubkey} />
</div>
