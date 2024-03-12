<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ExternalIdentities from "$lib/components/settings/ExternalIdentities.svelte";
    import Product from "$lib/components/stores/Product.svelte";
</script>

<svelte:head>
    <title>Get Verified</title>
</svelte:head>

<Titleh1>Get Verified</Titleh1>

<div class="grid">
    <p class="mx-auto">You need to <b>get verified</b> if you want to participate in Plebeian Market <b>auctions</b>. We use this as an <b>anti-spam</b>, <b>anti-troll</b> measure, to keep the auctions clean.</p>
    <p class="mx-auto">You'll need to <b>associate 2 external identities</b> to your Nostr account, and you'll need to <b>buy the Skin In The Game badge</b> if you don't have it yet.</p>
</div>

<Titleh1>External Identities</Titleh1>

<div class="flex">
    <div class="8/12 mx-auto">
        <ExternalIdentities />
    </div>
</div>

<!-- <Titleh1>Skin In The Game badge</Titleh1> -->

<div class="flex mt-20">
    <div class="8/12 mx-auto">
        <Product product_id={"04cafe6e-d1f0-4cce-9d0d-7af1a0f71953"} />
    </div>
</div>