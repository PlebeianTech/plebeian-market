<script lang="ts">
    export let shipping_from: string;
    export let shipping_estimate_domestic: string;
    export let shipping_estimate_worldwide: string;
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
            <span class="label-text">Domestic shipping estimate</span>
        </label>
        <input bind:value={shipping_estimate_domestic} type="text" name="shipping-estimate-domestic" placeholder="type anything" class="input input-bordered w-full max-w-xs" />
    </div>
    <div class="form-control w-1/2 max-w-xs ml-1">
        <label class="label" for="shipping-estimate-worldwide">
            <span class="label-text">Worldwide shipping estimate</span>
        </label>
        <input bind:value={shipping_estimate_worldwide} type="text" name="shipping-estimate-worldwide" placeholder="type anything" class="input input-bordered w-full max-w-xs" />
    </div>
</div>