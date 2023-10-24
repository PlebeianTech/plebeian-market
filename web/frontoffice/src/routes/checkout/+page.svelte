<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {NostrPublicKey, ShoppingCart, stalls, Error, Info} from "$sharedLib/stores";
    import {getLastOrderContactInformation, onImgError, refreshStalls} from "$lib/shopping";
    import {afterNavigate, goto} from "$app/navigation";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {waitAndShowLoginIfNotLoggedAlready, cleanShoppingCart} from "$sharedLib/utils";
    import {onDestroy} from "svelte";
    import ShippingContactInformation from "$lib/components/stores/ShippingContactInformation.svelte";
    import ShippingOptions from "$lib/components/stores/ShippingOptions.svelte";
    import {sendOrder} from "$sharedLib/nostr/utils";

    let name = null;
    let address = null;
    let message = null;

    let phone = null;
    let email = null;

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
                <ShippingOptions {stallId} {i} />

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
                            <p class="pr-2">
                                {product.price} x {product.orderQuantity} = {(product.orderQuantity ?? 0) * product.price} {#if product.currency}{product.currency}{/if}
                            </p>
                        </td>
                    </tr>
                {/each}
            {/each}
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
