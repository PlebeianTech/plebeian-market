<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {
        NostrPublicKey,
        ShoppingCart,
        stalls,
        Error,
        Info,
        userChosenCurrency
    } from "$sharedLib/stores";
    import {getLastOrderContactInformation, onImgError, refreshStalls} from "$lib/shopping";
    import {afterNavigate, goto} from "$app/navigation";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {waitAndShowLoginIfNotLoggedAlready, cleanShoppingCart} from "$sharedLib/utils";
    import {onDestroy} from "svelte";
    import ShippingContactInformation from "$lib/components/stores/ShippingContactInformation.svelte";
    import ShippingOptions from "$lib/components/stores/ShippingOptions.svelte";
    import {sendOrder} from "$sharedLib/nostr/utils";
    import CurrencyConverter from "$sharedLib/components/CurrencyConverter.svelte";
    import {convertCurrencies, getCurrencyInfo, removeDecimals} from "$sharedLib/currencies";

    let name = null;
    let address = null;
    let message = null;

    let phone = null;
    let email = null;

    $: total = 0;
    $: shippingCosts = 0;
    $: superTotal = 0;
    $: totalSats = 0;
    $: shippingCostsSats = 0;
    $: superTotalSats = 0;

    export async function buyNow() {
        console.log('---- buyNow start ----');

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

    const nostrPublicKeyUnsubscribe = NostrPublicKey.subscribe(async nostrPublicKeyValue => {
        if (nostrPublicKeyValue) {
            refreshStalls();

            const contactDetails = getLastOrderContactInformation();
            name = contactDetails.name ?? '';
            address = contactDetails.address ?? '';
            phone = contactDetails.phone ?? '';
            email = contactDetails.email ?? '';
        }
    });
    onDestroy(nostrPublicKeyUnsubscribe);

    afterNavigate(async () => {
        await waitAndShowLoginIfNotLoggedAlready();
    });

    async function calculateTotals() {
        total = 0;
        shippingCosts = 0;
        superTotal = 0;

        totalSats = 0;
        shippingCostsSats = 0;
        superTotalSats = 0;

        for (const [stallId, products] of [...$ShoppingCart.products]) {
            // Shipping cost
            if ($stalls?.stalls[stallId]) {
                for (const shippingOption of $stalls?.stalls[stallId].shipping) {
                    if ($stalls?.stalls[stallId].shippingOption === shippingOption.id) {
                        const convertedShippingCost = await convertCurrencies(shippingOption.cost, $stalls.stalls[stallId].currency);
                        if (convertedShippingCost) {
                            shippingCosts += convertedShippingCost.amount;
                            shippingCostsSats += convertedShippingCost.sats;
                        }
                    }
                }
            }


            // Product price
            for (const [productId, product] of [...products]) {
                const convertedProductTotal = await convertCurrencies(product.orderQuantity * product.price, product.currency);
                if (convertedProductTotal) {
                    total += convertedProductTotal.amount;
                    totalSats += convertedProductTotal.sats;
                }
            }
        }

        superTotal = total + shippingCosts;
        superTotalSats = totalSats + shippingCostsSats;
    }

    $: if ($ShoppingCart.products && $userChosenCurrency) {
        calculateTotals();
    }

    $: destinationCurrencyInfo = getCurrencyInfo($userChosenCurrency);
</script>

<svelte:head>
    <title>Checkout</title>
</svelte:head>

<Titleh1>Checkout</Titleh1>

{#if $ShoppingCart.summary.numProducts}
    <div class="md:grid justify-center md:mt-6 mb-10">
        <table class="w-fit md:w-full rounded border border-gray-400">
            <thead>
                <tr class="text-center">
                    <th>Name</th>
                    <th>Image</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {#each [...$ShoppingCart.products] as [stallId, products], i}
                    <ShippingOptions {stallId} {i} onchangeCallback={calculateTotals} />

                    {#each [...products] as [productId, product]}
                        <tr class="border-b border-gray-600 hover text-sm md:text-base">
                            <td class="py-1">
                                <p class="pl-3">{#if product.name}{product.name}{/if}</p>
                            </td>
                            <td class="py-1">
                                <div class="card shadow-xl w-20 md:w-20">
                                    <figure><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
                                </div>
                            </td>
                            <td class="py-1">
                                <p class="pr-2 flex">
                                    <CurrencyConverter
                                        amount={product.price}
                                        sourceCurrency={product.currency}
                                        satsClassStyle="mr-3"
                                    /> x {product.orderQuantity} = <CurrencyConverter
                                        amount={(product.orderQuantity ?? 0) * product.price}
                                        sourceCurrency={product.currency}
                                        satsClassStyle="ml-3"
                                        fiatClassStyle="ml-2 text-xs"
                                    />
                                </p>
                            </td>
                        </tr>
                    {/each}
                {/each}

                <tr>
                    <td colspan="3" class="bg-gray-300 dark:bg-gray-700 p-2 text-xs md:text-base">
                        <span class="mx-1 md:mx-2">Subtotal:</span>
                        <div class="float-right">
                            <span>{removeDecimals(totalSats, "SAT")} sat</span>
                            {#if $userChosenCurrency !== 'SAT'}
                                <p class="text-xs text-center">({destinationCurrencyInfo.prefix}{removeDecimals(total)}{destinationCurrencyInfo.suffix})</p>
                            {/if}
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan="3" class="bg-gray-300 dark:bg-gray-700 p-2 text-xs md:text-base">
                        <span class="mx-1 md:mx-2">Shipping:</span>
                        <div class="float-right">
                            <span>{removeDecimals(shippingCostsSats, "SAT")} sat</span>
                            {#if $userChosenCurrency !== 'SAT'}
                                <p class="text-xs text-center">({destinationCurrencyInfo.prefix}{removeDecimals(shippingCosts)}{destinationCurrencyInfo.suffix})</p>
                            {/if}
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan="3" class="bg-gray-300 dark:bg-gray-700 p-2 font-bold md:text-lg">
                        <span class="mx-1 md:mx-2">Total:</span>
                        <div class="float-right">
                            <span>~{removeDecimals(superTotalSats, "SAT")} sat</span>
                            {#if $userChosenCurrency !== 'SAT'}
                                <p class="text-xs text-center">(~{destinationCurrencyInfo.prefix}{removeDecimals(superTotal)}{destinationCurrencyInfo.suffix})</p>
                            {/if}
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <ShippingContactInformation
        bind:name={name}
        bind:address={address}
        bind:message={message}
        bind:email={email}
        bind:phone={phone}
        {buyNow}
    />

{:else}
    <div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">
        <div class="p-6 text-lg">
            <p>The shopping cart is empty.</p>
            <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stalls</a> and buy some products.</p>
        </div>

        <div class="card-actions justify-center" class:justify-end={$ShoppingCart.summary.numProducts}>
            <a class="btn btn-primary" href="/stalls">Continue shopping</a>
        </div>
    </div>
{/if}
