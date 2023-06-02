<script lang="ts">
    import QR from 'svelte-qr';
    export let paymentInfo;

    let copied = false;
    function copy() {
        navigator.clipboard.writeText(paymentInfo.link);
        copied = true;
    }
</script>

<div class="py-4 md:p-6 bg-white">
    <div class="qr">
        <a href="{paymentInfo.protocol}:{paymentInfo.link}">
            {#key `${paymentInfo.link}`}
                <QR text="{paymentInfo.link}" />
            {/key}
        </a>
    </div>

    <div class="mt-10 pb-0 flex justify-center items-center">
        <input value={paymentInfo.link} type="text" class="input input-bordered w-full max-w-xs px-0" disabled />
        <button class="btn ml-2 w-20" on:click={copy}>{#if copied}Copied{:else}Copy!{/if}</button>
    </div>

    {#if paymentInfo.protocol === 'lightning'}
        <div class="mt-10 pb-0 flex justify-center items-center">
            <ul class="list-disc list-outside text-xs md:text-sm">
                {#if paymentInfo.amount}
                    <li class="mb-3">You must send <b>{paymentInfo.amount} sats</b> to the seller</li>
                {/if}
                <li class="mb-3">If your wallet let you specify a <b>comment</b> while paying, put <b>{paymentInfo.orderId}</b></li>
                <li class="mb-3 md:mb-0">As the <b>payment goes directly to the seller</b> and <b>Lightning payments are private</b>,
                    we cannot tell you if the payment was successful. You must rely on your wallet for this.</li>
                <li class="md:hidden">You can <b>tap the QR code</b> to open your Lightning wallet.</li>
            </ul>
        </div>
    {/if}
</div>
