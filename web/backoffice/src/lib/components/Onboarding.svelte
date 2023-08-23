<script lang="ts">
    import StallSettings from "$lib/components/settings/Stall.svelte";
    import WalletSettings from "$lib/components/settings/Wallet.svelte";
    import EmailSettings from "$lib/components/settings/Email.svelte";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";
    import { user } from "$lib/stores";

    let step = 0;
    $: {
        if ($user) {
            if ($user.wallet === null || $user.wallet === "" || $user.lightningAddress === null || $user.lightningAddress === "") {
                step = 0;
            } else if ($user.stallName === null || $user.stallName === "") {
                step = 2;
            } else if ($user.email === null || $user.email === "" || !$user.emailVerified) {
                step = 3;
            }
        }
    }

</script>

<div class="mt-12">
    <div class="flex justify-center items-center">
        <ul class="steps steps-vertical lg:steps-horizontal">
            <li class="step" class:step-primary={step >= 1}>Wallet</li>
            <li class="step" class:step-primary={step >= 2}>Stall</li>
            <li class="step" class:step-primary={step >= 3}>Communications</li>
        </ul>
    </div>

    <div>
        {#if step === 0}
            <div class="w-full flex items-center justify-center mt-24">
                <div class="max-w-lg">
                    <InfoBox>
                        Do you want to be taken seriously on Plebeian Market?
                        <br />
                        We highly recommend you fill out your profile in full... Just 3 steps
                    </InfoBox>
                </div>
            </div>
            <div class="flex justify-center items-center mt-4 h-15">
                <button id="save" class="btn btn-primary btn-lg" on:click|preventDefault={() => step += 1}>Go!</button>
            </div>            
        {:else if step === 1}
            <WalletSettings />
        {:else if step === 2}
            <StallSettings />
        {:else if step === 3}
            <EmailSettings />
        {/if}
    </div>
</div>
