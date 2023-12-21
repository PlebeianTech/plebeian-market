<script lang="ts">
    import {NostrPublicKey} from "$sharedLib/stores";
    import Email from "$sharedLib/components/icons/Email.svelte";
    import Phone from "$sharedLib/components/icons/Phone.svelte";
    import Nostr from "$sharedLib/components/icons/Nostr.svelte";
    import {encodeNpub} from "$sharedLib/nostr/utils";

    export let isAuction = false;

    export let name = '';
    export let address = '';
    export let message = '';
    export let email = '';
    export let phone = '';

    export let buyNow = null;
</script>

<div class="flex flex-col md:flex-row w-full md:px-12 mt-12">
    <div class="grid flex-grow card w-full lg:w-2/4 p-4 md:p-8 gap-3 bg-base-300 rounded-box place-items-center">
        <h2 class="card-title">Shipping information</h2>
        <p>If you're purchasing a physical product, include all the info required so the merchant can send you the products.
            This information will be sent to the seller privately using Nostr messages from your account, so we don't
            even know what you put here. It's P2P between the seller and you.</p>

        <div class="form-control w-full max-w-xs mt-6">
            <label class="label">
                <span class="label-text">Name</span>
            </label>
            <input bind:value={name} type="text" class="input input-bordered input-warning w-full max-w-xs" />
        </div>

        <div class="form-control w-full max-w-xs">
            <label class="label">
                <span class="label-text">Shipping address</span>
            </label>
            <input bind:value={address} type="text" class="input input-bordered input-warning w-full max-w-xs" />
            <label class="label">
                <span class="label-text-alt">Full shipping address including country, etc.</span>
            </label>
        </div>

        <div class="form-control w-full max-w-xs">
            <label class="label">
                <span class="label-text">Message for the seller</span>
            </label>
            <textarea bind:value={message} class="textarea textarea-bordered input-warning" placeholder="Optional"></textarea>
        </div>
    </div>

    <div class="divider lg:divider-horizontal"></div>

    <div class="grid flex-grow card w-full lg:w-2/4 p-4 md:p-8 gap-3 bg-base-300 rounded-box place-items-center">
        <h2 class="card-title">Contact information</h2>
        <p>Nostr private messages is the default contact method, but you could also provide email or phone contact information if you prefer that way.</p>

        <!-- <div class="grid gap-5"> -->
        {#if $NostrPublicKey}
            <div class="form-control w-full max-w-xs">
                <label class="input-group input-group-lg">
                        <span>
                            <div class="w-9 h-9"><Nostr /></div>
                        </span>
                    <input value={encodeNpub($NostrPublicKey)} type="text" class="input input-bordered w-full max-w-lg font-xs text-xs" disabled />
                </label>
                <span class="label-text-alt">Hex: {$NostrPublicKey}</span>
            </div>
        {/if}
        <div class="form-control w-full max-w-xs">
            <label class="input-group input-group-lg">
                    <span>
                        <div class="w-9 h-9"><Email /></div>
                    </span>
                <input bind:value={email} type="text" class="input input-bordered input-warning w-full max-w-lg" />
            </label>
        </div>
        <div class="form-control w-full max-w-xs">
            <label class="input-group input-group-lg">
                    <span>
                        <div class="w-9 h-9"><Phone /></div>
                    </span>
                <input bind:value={phone} type="text" class="input input-bordered input-warning w-full max-w-lg" />
            </label>
        </div>
        <!-- </div> -->
    </div>
</div>

{#if buyNow}
    <div class="flex flex-col md:flex-row w-full md:px-12 mb-12">
        <div class="card-actions justify-center mt-10 md:mt-14 mx-auto">
            <a class="btn btn-success" class:btn-disabled={!$NostrPublicKey} on:click|preventDefault={buyNow}>{isAuction ? 'Send details' : 'Buy now'}</a>
        </div>
    </div>
{/if}