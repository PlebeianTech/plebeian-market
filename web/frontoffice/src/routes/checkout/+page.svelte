<script>
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {Error, Info, NostrPublicKey, privateMessages, ShoppingCart, stalls} from "$lib/stores";
    import {getLastOrderContactInformation, onImgError, refreshStalls} from "$lib/shopping";
    import { v4 as uuidv4 } from "uuid";
    import {sendPrivateMessage} from "$lib/services/nostr";
    import {goto} from "$app/navigation";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {requestLoginModal, waitAndShowLoginIfNotLoggedAlready} from "$lib/utils.ts";
    import {onDestroy} from "svelte";
    import ShippingContactInformation from "$lib/components/stores/ShippingContactInformation.svelte";
    import ShippingOptions from "$lib/components/stores/ShippingOptions.svelte";

    let name = null;
    let address = null;
    let message = null;

    let phone = null;
    let email = null;

    let shippingOption = null;

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

            const order = {
                id: uuidv4(),
                stall_id: stallId,
                type: 0,
                contact: {
                    nostr: $NostrPublicKey
                },
                items: orderItems,
                shipping_id: $stalls.stalls[stallId].shippingOption
            };

            if (name && name !== '') {
                order.name = name;
            }
            if (address && address !== '') {
                order.address = address;
            }
            if (message && message !== '') {
                order.message = message;
            }
            if (phone && phone !== '') {
                order.contact.phone = phone;
            }
            if (email && email !== '') {
                order.contact.email = email;
            }

            try {
                let messageOrder = JSON.stringify(order);
                console.log('************ jsonOrder:  ', order);

                await sendPrivateMessage($stalls.stalls[stallId].merchantPubkey, messageOrder,
                    async (relay) => {
                        console.log('-------- Order accepted by relay:', relay);

                        $ShoppingCart = {
                            products: new Map(),
                            summary: {
                                numProducts: 0,
                                totalQuantity: 0,
                                stalls: 0
                            }
                        };

                        await new Promise(resolve => setTimeout(resolve, 3500));

                        await goto('/orders');
                    }
                );

                Info.set('All the orders have been sent.');

                console.log('---- buyNow end ----');

            } catch (e) {
                Error.set('There was an error trying to buy the products. Check that you have a Nostr extension in the browser or you have generated the Nostr key correctly.');
                console.log('Error trying to buy the products:', e);
            }
        }
    }

    const nostrPublicKeyUnsubscribe = NostrPublicKey.subscribe(async nostrPublicKeyValue => {
        if (nostrPublicKeyValue) {
            refreshStalls();

            const contactDetails = getLastOrderContactInformation();
            name = contactDetails.name ?? '';
            address = contactDetails.address ?? '';
            phone = contactDetails.phone ?? '';
            email = contactDetails.email ?? '';
        } else {
            requestLoginModal();
        }
    });
    onDestroy(nostrPublicKeyUnsubscribe);
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
