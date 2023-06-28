<script>
    import {stalls} from "$lib/stores.ts";

    export let stallId;
    export let i;
</script>
<tr>
    <td colspan="3" class="bg-gray-300 dark:bg-gray-700 p-2">
        <p class="mx-2 md:mx-3 text-xs md:text-base">
            {#if i}
                Order #{i+1} -
            {/if}
            {#if $stalls.stalls[stallId] && $stalls.stalls[stallId].name}
                {$stalls.stalls[stallId].name}
            {/if}
        </p>

        <p class="mx-2 md:mx-3 mt-1">
            {#if $stalls.stalls[stallId] && $stalls.stalls[stallId].shipping}
                {#if $stalls.stalls[stallId].shipping.length > 1 && $stalls.stalls[stallId].shippingOption === '0'}
                    <div class="w-10 h-10 p-2 -mt-4 -mb-1 animate-bounce text-red-600 bg-white dark:bg-slate-800 ring-1 ring-slate-900/5 dark:ring-slate-200/20 shadow-lg rounded-full flex items-center justify-center mx-auto">
                        <svg fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" stroke="currentColor">
                            <path d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                        </svg>
                    </div>
                {/if}

                Shipping:
                <select bind:value={$stalls.stalls[stallId].shippingOption}
                        class="select select-sm text-xs md:text-sm max-w-lg md:ml-1 { ($stalls.stalls[stallId].shipping.length > 1 && $stalls.stalls[stallId].shippingOption === '0') ? 'select-error border-2' : 'select-bordered' }">

                    {#if $stalls.stalls[stallId].shipping.length > 1}
                        <option disabled selected value="0">Choose a shipping option:</option>
                    {/if}

                    {#each $stalls.stalls[stallId].shipping as shippingOption}
                        <option value="{shippingOption.id}">
                            {#if shippingOption.name}
                                {shippingOption.name} -
                            {/if}
                            {#if shippingOption.countries}
                                {#if !(shippingOption.countries.length === 1 && shippingOption.countries[0] === shippingOption.name)}
                                    ({shippingOption.countries.join(', ')}) -
                                {/if}
                            {/if}
                            {shippingOption.cost} {$stalls.stalls[stallId].currency}
                        </option>
                    {/each}
                </select>
            {:else}
                Loading shipping options...
            {/if}
        </p>
    </td>
</tr>
