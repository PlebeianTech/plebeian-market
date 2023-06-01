<script lang="ts">
    import QR from 'svelte-qr';
    export let protocol;
    export let address;

    let copied = false;
    function copy() {
        navigator.clipboard.writeText(address);
        copied = true;
    }
</script>

<div class="py-4 md:p-6 bg-white">
    <div class="qr">
        <a href="{protocol}:{address}">
            {#key `${address}`}
                <QR text="{address.toUpperCase()}" />
            {/key}
        </a>
    </div>

    <div class="mt-10 pb-0 flex justify-center items-center">
        <input value={address} type="text" class="input input-bordered w-full max-w-xs px-0" disabled />
        <button class="btn ml-2 w-20" on:click={copy}>{#if copied}Copied{:else}Copy!{/if}</button>
    </div>

    {#if protocol === 'lightning'}
        <div class="mt-10 pb-0 flex justify-center items-center">
            <ul class="list-disc list-outside text-xs md:text-sm">
                <li class="mb-3">If your wallet let you specify a <b>comment</b> while paying, put <b>#123</b></li>
                <li class="mb-3 md:mb-0">As the <b>payment goes directly to the seller</b> and <b>Lightning payments are private</b>,
                    we cannot tell you if the payment was successful. You must rely on your wallet for this.</li>
                <li class="md:hidden">You can <b>tap the QR code</b> to open your Lightning wallet.</li>
            </ul>
        </div>
    {/if}
</div>
