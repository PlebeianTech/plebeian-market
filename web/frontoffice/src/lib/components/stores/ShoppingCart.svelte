<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {Error, Info, NostrPublicKey, ShoppingCart, stalls, userChosenCurrency} from "$sharedLib/stores";
    import {deleteFromCart, onImgError} from "$lib/shopping";
    import Trash from "$sharedLib/components/icons/Trash.svelte";
    import Quantity from "./Quantity.svelte";
    import CurrencyConverter from "$sharedLib/components/CurrencyConverter.svelte";
    import {cleanShoppingCart, waitAndShowLoginIfNotLoggedAlready} from "$sharedLib/utils";
    import {convertCurrencies, getCurrencyInfo, removeDecimals} from "$sharedLib/currencies";
    import ShippingContactInformation from "$lib/components/stores/ShippingContactInformation.svelte";
    import {sendOrder} from "$sharedLib/nostr/utils";
    import ShippingOptions from "$lib/components/stores/ShippingOptions.svelte";
    import {goto} from "$app/navigation";

    export let compact = false;

    let name = null;
    let address = null;
    let message = null;

    let phone = null;
    let email = null;

    let showCheckout = false;

    $: total = 0;
    $: shippingCosts = 0;
    $: superTotal = 0;
    $: totalSats = 0;
    $: shippingCostsSats = 0;
    $: superTotalSats = 0;

    $: {
        // When you are viewing the full-featured-cart, you'll run this code twice: one for the compact cart
        // that is always visible at the NavBar, and the other one for the Cart page.
        //
        // It seems one of the runs interferes with the other one, and they enter a loop. Probably have
        // something to do with the reactivity: you're updating a store when there are changes in the store,
        // and then you're making calls to the same store at the same time...
        //
        // This "if" makes that this runs just once when viewing the full-featured shopping cart.

        if (compact) {
            let numProducts = 0;
            let totalQuantity = 0;
            let stalls = 0;

            for (const [_, stall] of $ShoppingCart.products) {
                stalls++;
                for (const [_, product] of stall) {
                    numProducts++;
                    totalQuantity = totalQuantity + product.orderQuantity;
                }
            }

            $ShoppingCart.summary = {
                numProducts: numProducts,
                totalQuantity: totalQuantity,
                stalls: stalls
            };
        }
    }

    export async function buyNow() {
        if (!await waitAndShowLoginIfNotLoggedAlready()) {
            return;
        }

        let checkOk = true;

        for (const [stallId, stall] of $ShoppingCart.products) {
            if ($stalls.stalls[stallId].shippingOption === '0') {
                checkOk = false;
                break;
            }
        }

        if (!checkOk) {
            Error.set('You must choose shipping options for each order.');
            return;
        }

        for (const [stallId, stall] of $ShoppingCart.products) {
            let orderItems = [];
            for (const [productId, product] of stall) {
                orderItems.push({
                    product_id: productId,
                    quantity: product.orderQuantity
                });
            }

            // If there is no shippingOption chosen by the user and there is only
            // one shipping option, it's because we didn't even show the list to
            // the user, so let's auto-choose the only shipping option available
            if (!$stalls.stalls[stallId].shippingOption && $stalls.stalls[stallId].shipping.length === 1) {
                $stalls.stalls[stallId].shippingOption = $stalls.stalls[stallId].shipping[0].id;
            }

            await sendOrder(stallId, orderItems, null, name, address, message, phone, email);
        }

        Info.set('All the orders have been sent.');

        cleanShoppingCart();

        await new Promise(resolve => setTimeout(resolve, 1500));

        await goto('/orders');
    }

    async function calculateShippingAndTotals() {
        // Work with local variables first, then save to external variables
        // This reduces flickering because external (reactive) variables
        // are not updated so often, and prevents miscalculations if the
        // function is called twice for any reason (it happens)
        let totalTemp = 0;
        let shippingCostsTemp = 0;
        let superTotalTemp = 0;

        let totalSatsTemp = 0;
        let shippingCostsSatsTemp = 0;
        let superTotalSatsTemp = 0;

        for (const [stallId, products] of [...$ShoppingCart.products]) {
            // Stall shipping cost
            if ($stalls?.stalls[stallId]) {
                for (const shippingOption of $stalls?.stalls[stallId].shipping) {
                    if ($stalls?.stalls[stallId].shippingOption === shippingOption.id) {
                        const convertedShippingCost = await convertCurrencies(shippingOption.cost, $stalls.stalls[stallId].currency);
                        if (convertedShippingCost) {
                            shippingCostsTemp += convertedShippingCost.amount;
                            shippingCostsSatsTemp += convertedShippingCost.sats;
                        }
                    }
                }
            }

            // Product shipping cost
            for (const [productId, product] of [...products]) {
                if (product.shipping) {
                    for (const productShippingOption of product.shipping) {
                        if (!productShippingOption.cost) {
                            continue;
                        }

                        if (productShippingOption.id && $stalls?.stalls[stallId] && $stalls?.stalls[stallId].shippingOption === productShippingOption.id && productShippingOption.cost) {
                            const convertedShippingCost = await convertCurrencies(productShippingOption.cost, $stalls.stalls[stallId].currency);
                            if (convertedShippingCost) {
                                shippingCostsTemp += convertedShippingCost.amount;
                                shippingCostsSatsTemp += convertedShippingCost.sats;
                            }
                        }
                    }
                }
            }

            // Product price
            for (const [productId, product] of [...products]) {
                const convertedProductTotal = await convertCurrencies(product.orderQuantity * product.price, product.currency);
                if (convertedProductTotal) {
                    totalTemp += convertedProductTotal.amount;
                    totalSatsTemp += convertedProductTotal.sats;
                }
            }
        }

        superTotalTemp = totalTemp + shippingCostsTemp;
        superTotalSatsTemp = totalSatsTemp + shippingCostsSatsTemp;

        // Copy to external vars
        total = totalTemp;
        shippingCosts = shippingCostsTemp;
        superTotal = superTotalTemp;

        totalSats = totalSatsTemp;
        shippingCostsSats = shippingCostsSatsTemp;
        superTotalSats = superTotalSatsTemp;
    }

    async function calculateShippingOptions() {
        for (const [stallId, products] of [...$ShoppingCart.products]) {
            if ($stalls.stalls[stallId]) {
                $stalls.stalls[stallId].allShippingOptions = [];

                // Stall shipping options
                for (const stallShippingOption of $stalls?.stalls[stallId].shipping) {
                    $stalls.stalls[stallId].allShippingOptions.push(stallShippingOption);
                }

                // Product shipping options
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

    $: if (!compact && $ShoppingCart.products && $userChosenCurrency && $stalls && !$stalls.fetching) {
        calculateShippingOptions();
        calculateShippingAndTotals();
    }

    $: destinationCurrencyInfo = getCurrencyInfo($userChosenCurrency);

    /*
    afterNavigate(async () => {
        await waitAndShowLoginIfNotLoggedAlready();
    });
    */
</script>

<div class="md:grid justify-center">
{#if $ShoppingCart.summary.numProducts && $stalls && $stalls.stalls}
    <!-- Desktop -->
    <table class="hidden md:block table table-auto w-full {compact ? 'table-md' : 'border rounded border-gray-400'}" >
        <thead>
            <tr class="text-center">
                <th>Name</th>
                {#if !compact}
                    <th>Description</th>
                {/if}
                <th>Price</th>
                <th>Quantity</th>
                <th>Image</th>
                <th>Total</th>
                <th></th>
            </tr>
        </thead>

        <tbody>
            {#each [...$ShoppingCart.products] as [stallId, products], i}
                {#if $stalls.stalls[stallId]}
                    {#if !compact}
                        <ShippingOptions {stallId} {i} colspan={compact ? '6' : '7'} onchangeCallback={calculateShippingAndTotals} />
                    {/if}

                    {#each [...products] as [_, product]}
                        <tr>
                            <th>{#if product.name}<a href="/product/{product.id}">{product.name}</a>{/if}</th>
                            {#if !compact}
                                <td>{#if product.description}{product.description.substring(0,80)}{#if product.description.length > 80}...{/if}{/if}</td>
                            {/if}
                            <td class="text-center">
                                <CurrencyConverter
                                    amount={product.price}
                                    sourceCurrency={product.currency}
                                />
                            </td>
                            <td>
                                <Quantity bind:quantity={product.orderQuantity} maxStock={product.quantity} {compact} />
                            </td>
                            <td>
                                <div class="card shadow-xl { compact ? 'w-16' : 'w-32'}">
                                    <img class:rounded-xl={!compact} src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} />
                                </div>
                            </td>
                            <td class="text-center">
                                <CurrencyConverter
                                    amount={(product.orderQuantity ?? 0) * product.price}
                                    sourceCurrency={product.currency}
                                />
                            </td>

                            <th class="cursor-pointer mr-4" on:click={() => deleteFromCart(stallId, product.id)}>
                                <div class="w-5 h-5 tooltip tooltip-error" data-tip="{ compact ? 'Remove product' : 'Remove product from shopping cart'}"><Trash /></div>
                            </th>
                        </tr>
                    {/each}

                {:else}
                    <tr>Loading stall information...</tr>
                {/if}
            {/each}

            {#if !compact}
                {#if shippingCostsSats}
                    <tr>
                        <td colspan="{compact ? 6 : 7}" class="bg-gray-300 dark:bg-gray-700 p-2 md:text-base">
                            <span class="md:mx-2">Subtotal:</span>
                            <div class="float-right md:mx-2">
                                <span>{removeDecimals(totalSats, "SAT")} sat</span>
                                {#if $userChosenCurrency !== 'SAT'}
                                    <p class="text-xs text-center">({destinationCurrencyInfo.prefix}{removeDecimals(total)}{destinationCurrencyInfo.suffix})</p>
                                {/if}
                            </div>
                        </td>
                    </tr>
                {/if}
                <tr>
                    <td colspan="{compact ? 6 : 7}" class="bg-gray-300 dark:bg-gray-700 p-2 md:text-base">
                        <span class="md:mx-2">Shipping:</span>
                        <div class="float-right md:mx-2">
                            {#if superTotalSats}
                                <span>{removeDecimals(shippingCostsSats, "SAT")} sat</span>
                                {#if $userChosenCurrency !== 'SAT' && shippingCostsSats > 0}
                                    <p class="text-xs text-center">({destinationCurrencyInfo.prefix}{removeDecimals(shippingCosts)}{destinationCurrencyInfo.suffix})</p>
                                {/if}
                            {:else}
                                <span class="loading loading-bars w-6"></span>
                            {/if}
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan="{compact ? 6 : 7}" class="bg-gray-300 dark:bg-gray-700 p-2 font-bold md:text-lg">
                        <span class="md:mx-2">Total:</span>
                        <div class="float-right md:mx-2">
                            {#if superTotalSats}
                                <span>~{removeDecimals(superTotalSats, "SAT")} sat</span>
                                {#if $userChosenCurrency !== 'SAT'}
                                    <p class="text-xs text-center">(~{destinationCurrencyInfo.prefix}{removeDecimals(superTotal)}{destinationCurrencyInfo.suffix})</p>
                                {/if}
                            {:else}
                                <span class="loading loading-bars w-6"></span>
                            {/if}
                        </div>
                    </td>
                </tr>
            {/if}
        </tbody>
    </table>

    <!-- Mobile -->
    <table class="table table-auto w-full md:hidden text-left {compact ? 'table-sm' : 'border rounded border-gray-400'}">
        <thead>
            <tr class="text-center">
                <th class="text-left pl-1 pr-0">Name</th>
                <th class="px-0">Price</th>
                <th class="px-1">Quantity</th>
                <th class="px-0">Total</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            {#each [...$ShoppingCart.products] as [stallId, products], i}
                {#if $stalls.stalls[stallId]}
                    {#if !compact}
                        <ShippingOptions {stallId} {i} colspan={compact ? '6' : '7'} onchangeCallback={calculateShippingAndTotals} />
                    {/if}

                    {#each [...products] as [_, product]}
                        <tr class="text-xs text-center">
                            <th class="text-left text-xs pl-1 pr-0">{#if product.name}<a href="/product/{product.id}">{product.name}</a>{/if}</th>
                            <td class="px-0">
                                <CurrencyConverter
                                    amount={product.price}
                                    sourceCurrency={product.currency}
                                />
                            </td>
                            <td class="px-1">
                                <Quantity bind:quantity={product.orderQuantity} maxStock={product.quantity} {compact} />
                            </td>
                            <td class="px-0">
                                <CurrencyConverter
                                    amount={(product.orderQuantity ?? 0) * product.price}
                                    sourceCurrency={product.currency}
                                />
                            </td>
                            <td class="pl-1 pr-1" on:click={() => deleteFromCart(stallId, product.id)}>
                                <div class="w-5 h-5"><Trash /></div>
                            </td>
                        </tr>
                    {/each}
                {:else}
                    <tr>Loading stall information...</tr>
                {/if}
            {/each}

            {#if !compact}
                {#if shippingCostsSats}
                    <tr>
                        <td colspan="{compact ? 6 : 7}" class="bg-gray-300 dark:bg-gray-700 p-2 text-xs">
                            <span class="mx-1">Subtotal:</span>
                            <div class="float-right">
                                <span>{removeDecimals(totalSats, "SAT")} sat</span>
                                {#if $userChosenCurrency !== 'SAT'}
                                    <p class="text-xs text-center">({destinationCurrencyInfo.prefix}{removeDecimals(total)}{destinationCurrencyInfo.suffix})</p>
                                {/if}
                            </div>
                        </td>
                    </tr>
                {/if}
                <tr>
                    <td colspan="{compact ? 6 : 7}" class="bg-gray-300 dark:bg-gray-700 p-2 text-xs">
                        <span class="mx-1">Shipping:</span>
                        <div class="float-right">
                            {#if superTotalSats}
                                <span>{removeDecimals(shippingCostsSats, "SAT")} sat</span>
                                {#if $userChosenCurrency !== 'SAT' && shippingCostsSats > 0}
                                    <p class="text-xs text-center">({destinationCurrencyInfo.prefix}{removeDecimals(shippingCosts)}{destinationCurrencyInfo.suffix})</p>
                                {/if}
                            {:else}
                                <span class="loading loading-bars w-6"></span>
                            {/if}
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan="{compact ? 6 : 7}" class="bg-gray-300 dark:bg-gray-700 p-2 font-bold">
                        <span class="mx-1">Total:</span>
                        <div class="float-right">
                            {#if superTotalSats}
                                <span>~{removeDecimals(superTotalSats, "SAT")} sat</span>
                                {#if $userChosenCurrency !== 'SAT'}
                                    <p class="text-xs text-center">(~{destinationCurrencyInfo.prefix}{removeDecimals(superTotal)}{destinationCurrencyInfo.suffix})</p>
                                {/if}
                            {:else}
                                <span class="loading loading-bars w-6"></span>
                            {/if}
                        </div>
                    </td>
                </tr>
            {/if}
        </tbody>
    </table>

{:else}
    <div class="p-6 text-lg" class:w-64={compact}>
        <p>The shopping cart is empty.</p>
        <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stalls</a> and buy some products.</p>
        <p class="mt-4">You can check the <a class="text-blue-500" href="/orders">Orders</a> screen to check the status of your orders.</p>
    </div>
{/if}
</div>

{#if !compact && showCheckout && $ShoppingCart.summary.numProducts && $stalls && $stalls.stalls}
    <ShippingContactInformation
        bind:name={name}
        bind:address={address}
        bind:message={message}
        bind:email={email}
        bind:phone={phone}
    />
{/if}

<div class="md:grid justify-center">
    {#if compact}
        {#if $ShoppingCart.summary.numProducts && $stalls && $stalls.stalls}
            <div class="mt-6 card-actions justify-center">
                <a class="btn btn-primary btn-block" href="/cart">See cart details</a>
            </div>
        {/if}
    {:else}
        <div class="mt-6 card-actions justify-center">
            <a class="btn btn-info mr-1" href="/planet">Continue shopping</a>
            {#if $ShoppingCart.summary.numProducts && $stalls && $stalls.stalls}
                {#if !showCheckout}
                    <a class="btn btn-success" on:click={() => {calculateShippingAndTotals(); showCheckout = true}} href={null}>Checkout</a>
                {:else}
                    <a class="btn btn-success" class:btn-disabled={!$NostrPublicKey} on:click|preventDefault={buyNow} href={null}>Buy now</a>
                {/if}
            {/if}
        </div>
    {/if}
</div>