<script lang="ts">
    export let protocol;
    export let address;
    export let qr;

    let copied = false;
    function copy() {
        navigator.clipboard.writeText(address);
        copied = true;
    }
</script>

<div class="qr"><a href="{protocol}:{address}">{@html qr}</a></div>
<div class="mt-10 pb-4 flex justify-center items-center">
    <input value={address} type="text" class="input input-bordered w-full max-w-xs" disabled />
    <button class="btn ml-2 w-20" on:click={copy}>{#if copied}Copied{:else}Copy!{/if}</button>
</div>