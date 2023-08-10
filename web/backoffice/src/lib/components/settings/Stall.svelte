<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { ErrorHandler, putProfile } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { Info, token } from "$sharedLib/stores";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";

    export let onSave: () => void = () => {};

    let stallName: string = "";
    let stallDescription: string = "";
    let shippingFrom: string = "";
    let shippingDomesticUsd: number = 0;
    let shippingWorldwideUsd: number = 0;

    $: isValidName = stallName !== null && stallName !== "";

    $: saveButtonActive = !saving && $user && isValidName && (stallName !== $user.stallName || stallDescription !== $user.stallDescription || shippingFrom !== $user.shippingFrom || shippingDomesticUsd !== $user.shippingDomesticUsd || shippingWorldwideUsd !== $user.shippingWorldwideUsd);

    let saving = false;
    function save() {
        saving = true;
        putProfile($token, {stallName, stallDescription, shippingFrom, shippingDomesticUsd, shippingWorldwideUsd},
            (u, n) => {
                user.set(u);
                if (n) {
                    Info.set("Your stall has been published to Nostr!");
                } else {
                    Info.set("Your stall details have been saved!");
                }
                stallName = u.stallName || "";
                stallDescription = u.stallDescription || "";
                shippingFrom = u.shippingFrom || "";
                shippingDomesticUsd = u.shippingDomesticUsd || 0;
                shippingWorldwideUsd = u.shippingWorldwideUsd || 0;
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            stallName = $user.stallName || "";
            stallDescription = $user.stallDescription || "";
            shippingFrom = $user.shippingFrom || "";
            shippingDomesticUsd = $user.shippingDomesticUsd || 0;
            shippingWorldwideUsd = $user.shippingWorldwideUsd || 0;
        }
    });
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>My Stall</li>
        </ul>
    </div>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div class="form-control w-full">
        <label class="label" for="stallName">
            <span class="label-text">Title</span>
        </label>
        <input bind:value={stallName} id="stallName" name="stallName" type="text" class="input input-bordered input-md w-full" />
    </div>
</div>

<div class="w-full flex items-center justify-center my-8 gap-2 flex-col md:flex-row">
    <div class="form-control w-full">
        <label class="label" for="shippingFrom">
            <span class="label-text">Shipping from</span>
            <div class="tooltip tooltip-left" data-tip="We use this to provide shipping options to the buyers. Be as vague or as specific as you want / need to be.">
                <InfoIcon />
            </div>
        </label>
        <input bind:value={shippingFrom} id="shippingFrom" name="shippingFrom" type="text" class="input input-bordered input-md w-full" />
    </div>

    <div class="form-control w-full">
        <label class="label" for="shippingDomesticUsd">
            <span class="label-text">Domestic ($)</span>
            <div class="tooltip tooltip-left" data-tip="How much does shipping cost within the area specified as shipping from?">
                <InfoIcon />
            </div>
        </label>
        <input bind:value={shippingDomesticUsd} type="number" name="shippingDomesticUsd" class="input input-bordered w-full w-full" />
    </div>

    <div class="form-control w-full">
        <label class="label" for="shippingWorldwideUsd">
            <span class="label-text">Worldwide ($)</span>
            <div class="tooltip tooltip-left" data-tip="How much does shipping cost outside the area you are shipping?">
                <InfoIcon />
            </div>
        </label>
        <input bind:value={shippingWorldwideUsd} type="number" name="shippingWorldwideUsd" class="input input-bordered w-full w-full" />
    </div>
</div>

<div class="form-control mt-2">
    <label class="label" for="description">
        <span class="label-text">Description</span>
    </label>
    <textarea bind:value={stallDescription} rows="6" class="textarea textarea-bordered h-48"></textarea>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    <button id="save-profile" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={save}>Save</button>
</div>
