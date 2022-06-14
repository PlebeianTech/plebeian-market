<script lang="ts">
    export let lnurl;
    export let qr;

    let copied = false;
    function copy() {
        navigator.clipboard.writeText(lnurl);
        copied = true;
    }
</script>

<div class="qr glowbox"><a href="lightning:{lnurl}">{@html qr}</a></div>
<div class="mt-10 pb-4 flex justify-center items-center">
    <input value={lnurl} type="text" class="input input-bordered w-full max-w-xs" disabled />
    <button class="btn ml-2 w-20" on:click={copy}>{#if copied}Copied{:else}Copy!{/if}</button>
</div>