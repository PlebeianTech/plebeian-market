<script lang="ts">
    import { user } from "$lib/stores";
    import type { Item } from "$lib/types/item";
    import InfoIcon from "$sharedLib/components/icons/Info.svelte";

    export let item: Item;
</script>

<div class="card bg-base-100 mt-4 p-4">
    <h3 class="card-title">Shipping</h3>
    <p class="mt-3">Per-order shipping (set in the <a class="link" href="/admin/account/settings">stall settings</a>)<br />
        Domestic: <b>${$user?.shippingDomesticUsd}</b><br />
        Worldwide: <b>${$user?.shippingWorldwideUsd}</b>
    </p>
    <p class="my-4 text-3xl">+</p>
    <p class="mt-3">Extra shipping for this item</p>
    <div class="flex">
        <div class="form-control w-1/2 max-w-xs mr-1">
            <label class="label" for="extraShippingDomesticUsd">
                <span class="label-text">Domestic ($)</span>
                <div class="tooltip tooltip-left" data-tip="Extra cost to add to the stall-level domestic shipping">
                    <InfoIcon />
                </div>
            </label>
            <input bind:value={item.extra_shipping_domestic_usd} type="number" name="extraShippingDomesticUsd" class="input input-bordered w-full w-full" />
        </div>
        <div class="form-control w-1/2 max-w-xs ml-1">
            <label class="label" for="extraShippingWorldwideUsd">
                <span class="label-text">Worldwide ($)</span>
                <div class="tooltip tooltip-left" data-tip="Extra cost to add to the stall-level worldwide shipping">
                    <InfoIcon />
                </div>
            </label>
            <input bind:value={item.extra_shipping_worldwide_usd} type="number" name="extraShippingWorldwideUsd" class="input input-bordered w-full w-full" />
        </div>
    </div>
</div>