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

<div class="p-6 bg-white">
    <div class="qr">
        <a href="{protocol}:{address}">
            {#key `${address}`}
                <QR text="{address}" />
            {/key}
        </a>
    </div>
    <div class="mt-10 pb-4 flex justify-center items-center">
        <input value={address} type="text" class="input input-bordered w-full max-w-xs" disabled />
        <button class="btn ml-2 w-20" on:click={copy}>{#if copied}Copied{:else}Copy!{/if}</button>
    </div>
</div>
