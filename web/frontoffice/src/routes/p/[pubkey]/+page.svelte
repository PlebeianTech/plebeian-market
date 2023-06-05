<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ResumeView from "$lib/components/resume/View.svelte";
    import StallsBrowser from "$lib/components/stores/Browse.svelte";
    import {NostrPublicKey} from "$lib/stores";

    /** @type {import('./$types').PageData} */
    export let data;
</script>

{#if data.pubkey === $NostrPublicKey}
    <Titleh1>Your profile</Titleh1>
{:else}
    <Titleh1>Profile of user</Titleh1>
{/if}

<StallsBrowser merchantPubkey={data.pubkey}></StallsBrowser>

<ResumeView pubkey={data.pubkey} />
