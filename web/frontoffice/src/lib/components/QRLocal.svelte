<script lang="ts">
    import QR from 'svelte-qr';
    export let paymentInfo;

    let copied = false;
    function copy() {
        navigator.clipboard.writeText(paymentInfo.link);
        copied = true;
    }
</script>


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



