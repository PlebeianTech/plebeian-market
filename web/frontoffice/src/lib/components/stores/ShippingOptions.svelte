<script lang="ts">
    import {ShoppingCart, stalls} from "$sharedLib/stores";
    import CurrencyConverter from "$sharedLib/components/CurrencyConverter.svelte";
    import {onMount} from "svelte";

    export let stallId;
    export let i: number;
    export let colspan = "3";
    export let inAuctionView = false;
    export let auctionProduct = null;
    export let onchangeCallback = () => {};

    async function calculateShippingOptions() {
        // Stall shipping options
        if ($stalls.stalls[stallId]) {
            $stalls.stalls[stallId].allShippingOptions = [];

            for (const stallShippingOption of $stalls?.stalls[stallId].shipping) {
                $stalls.stalls[stallId].allShippingOptions.push(stallShippingOption);
            }
        }

        // Product shipping options: Fixed price / shopping cart products
        if (!inAuctionView) {
            if ($stalls.stalls[stallId]) {
                for (const [stall_id, products] of [...$ShoppingCart.products]) {
                    if ($stalls.stalls[stall_id] && stall_id == stallId) {
                        for (const [productId, product] of [...products]) {
                            product.shipping?.forEach((productShippingOption) => {
                                if (productShippingOption.id) {
                                    let idAlreadyExists = false;

                                    $stalls.stalls[stallId].allShippingOptions.forEach((shippingOption) => {
                                        if (shippingOption.id === productShippingOption.id) {
                                            idAlreadyExists = true;
                                        }
                                    });

                                    if (!idAlreadyExists) {
                                        $stalls.stalls[stallId].allShippingOptions.push(productShippingOption);
                                    }
                                }
                            });
                        }
                    }
                }
            }

        // Product shipping options: auctions
        } else {
            auctionProduct.shipping?.forEach((productShippingOption) => {
                if (productShippingOption.id) {
                    let idAlreadyExists = false;

                    $stalls.stalls[stallId].allShippingOptions.forEach((shippingOption) => {
                        if (shippingOption.id === productShippingOption.id) {
                            idAlreadyExists = true;
                        }
                    });

                    if (!idAlreadyExists) {
                        $stalls.stalls[stallId].allShippingOptions.push(productShippingOption);
                    }
                }
            });
        }
    }

    $: if ($ShoppingCart.products) {
        calculateShippingOptions();
    }
    onMount(async () => {
        calculateShippingOptions();
    });
</script>
<tr>
    <td colspan="{colspan}" class="bg-gray-300 dark:bg-gray-700 p-2">
        <p class="md:mx-3 text-xs md:text-base">
            {#if i}
                Order #{i+1} -
            {/if}
            {#if $stalls?.stalls[stallId] && $stalls.stalls[stallId].name}
                <a href="/p/{$stalls.stalls[stallId].merchantPubkey}/stall/{$stalls.stalls[stallId].id}">
                    {$stalls.stalls[stallId].name}
                </a>
            {/if}
        </p>

        {#if !$stalls?.stalls[stallId] || !$stalls.stalls[stallId].allShippingOptions}
            <p class="md:mx-3 mt-1">Loading shipping options...</p>
        {:else if !($stalls.stalls[stallId].allShippingOptions.length === 1 && $stalls.stalls[stallId].allShippingOptions[0].cost === 0)}
            <div class="md:mx-3 mt-1 w-fit">
                {#if $stalls.stalls[stallId].allShippingOptions.length > 1 && $stalls.stalls[stallId].shippingOption === '0'}
                    <div class="flex mx-auto size-10 p-2 -mt-4 -mb-1 animate-bounce text-red-600 bg-white dark:bg-slate-800 ring-1 ring-slate-900/5 dark:ring-slate-200/20 shadow-lg rounded-full">
                        <svg fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" stroke="currentColor">
                            <path d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                        </svg>
                    </div>
                {/if}

                Shipping:
                <select bind:value={$stalls.stalls[stallId].shippingOption} on:change={onchangeCallback}
                        class="select select-sm text-xs md:text-sm max-w-lg md:ml-1 { ($stalls.stalls[stallId].allShippingOptions.length > 1 && $stalls.stalls[stallId].shippingOption === '0') ? 'select-error border-2' : 'select-bordered' }">

                    {#if $stalls.stalls[stallId].allShippingOptions.length > 1}
                        <option disabled selected value="0">Choose a shipping option:</option>
                    {/if}

                    {#each $stalls.stalls[stallId].allShippingOptions as shippingOption}
                        <option value="{shippingOption.id}">
                            {#if shippingOption.name}
                                {shippingOption.name} -
                            {:else}
                                {#if shippingOption.id === 'WORLD'}
                                    Worldwide -
                                {:else}
                                    Domestic -
                                {/if}
                            {/if}
                            {#if shippingOption.countries}
                                {#if !(shippingOption.countries.length === 1 && shippingOption.countries[0] === shippingOption.name)}
                                    ({shippingOption.countries.join(', ')}) -
                                {/if}
                            {/if}
                            <CurrencyConverter
                                amount={shippingOption.cost}
                                sourceCurrency={$stalls.stalls[stallId].currency}
                            />
                        </option>
                    {/each}
                </select>
            </div>
        {/if}
    </td>
</tr>
