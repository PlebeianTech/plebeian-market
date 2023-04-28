<script lang="ts">
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";

    export let shipping_from: string;
    export let shipping_domestic_usd: number;
    export let shipping_worldwide_usd: number;
</script>

<div class="form-control w-full max-w-xs mt-3">
    <label class="label" for="shipping_from">
        <span class="label-text">Shipping from</span>
    </label>
    <input bind:value={shipping_from} type="text" name="shipping_from" placeholder="type anything" class="input input-bordered w-full max-w-xs" />
</div>
<div class="flex mt-3">
    <div class="form-control w-1/2 max-w-xs mr-1">
        <label class="label" for="shipping-estimate-domestic">
            <span class="label-text">Domestic shipping ($)</span>
        </label>
        <input bind:value={shipping_domestic_usd} type="number" name="shipping-domestic-usd" class="input input-bordered w-full max-w-xs" />
        <label class="label" for="shipping-domestic-usd">
            <span class="label-text-alt"><AmountFormatter usdAmount={shipping_domestic_usd} format={AmountFormat.Sats} /></span>
            <span class="label-text-alt"></span>
        </label>
    </div>
    <div class="form-control w-1/2 max-w-xs ml-1">
        <label class="label" for="shipping-worldwide-usd">
            <span class="label-text">Worldwide shipping ($)</span>
        </label>
        <input bind:value={shipping_worldwide_usd} type="number" name="shipping-worldwide-usd" class="input input-bordered w-full max-w-xs" />
        <label class="label" for="shipping-worldwide-usd">
            <span class="label-text-alt"><AmountFormatter usdAmount={shipping_worldwide_usd} format={AmountFormat.Sats} /></span>
            <span class="label-text-alt"></span>
        </label>
    </div>
</div>