<script lang="ts">
    import StallSettings from "$lib/components/settings/Stall.svelte";
    import WalletSettings from "$lib/components/settings/Wallet.svelte";

    let step = 0;
</script>

<div class="mt-12">
    <div class="flex justify-center items-center">
        <ul class="steps steps-vertical lg:steps-horizontal">
            <li class="step" class:step-primary={step >= 0}>Set up wallet</li>
            <li class="step" class:step-primary={step >= 1}>Set up stall</li>
            <li class="step">Add your first product</li>
        </ul>
    </div>

    <div>
        {#if step === 0}
            <WalletSettings onSave={() => step += 1} />
        {:else if step === 1}
            <StallSettings onSave={() => step += 1} />
        {/if}
    </div>
</div>
