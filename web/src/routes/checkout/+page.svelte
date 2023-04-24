<script>
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Email from "$lib/components/icons/Email.svelte";
    import Phone from "$lib/components/icons/Phone.svelte";
    import Nostr from "$lib/components/icons/Nostr.svelte";
    import {Error, Info, NostrPool, ShoppingCart} from "$lib/stores";
    import {onImgError} from "$lib/shopping";
    import {onMount} from "svelte";
    import { v4 as uuidv4 } from "uuid";
    import {getStalls, sendPrivateMessage} from "$lib/services/nostr.ts";
    import {getFirstTagValue} from "$lib/nostr/utils.ts";
    import {goto} from "$app/navigation";

    let name = null;
    let address = null;
    let message = null;

    let nostrPublicKey = 'fh483279rgf7h2g2ibf76282bo9hf8yv72tv7i';
    let phone = null;
    let email = null;

    $: stalls = [];
    let merchantPubkeys = [];

    export function buyNow() {
        console.log('---- buyNow start ----');

        // console.log('---- stalls: ', stalls);

        let checkOk = true;

        for (const [stallId, stall] of $ShoppingCart.products) {
            if (stalls[stallId].shippingOption === '0') {
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
                type: "0",
                contact: {
                    nostr: nostrPublicKey
                },
                items: orderItems,
                shipping_id: stalls[stallId].shippingOption
            };

            if (name) {
                order.name = name;
            }
            if (address) {
                order.address = address;
            }
            if (message) {
                order.message = message;
            }
            if (phone) {
                order.contact.phone = phone;
            }
            if (email) {
                order.contact.email = email;
            }

            let messageOrder = JSON.stringify(order);
            // console.log('************ jsonOrder (stallId='+stallId+'):  ', order);

            sendPrivateMessage($NostrPool, stalls[stallId].merchantPubkey, messageOrder,
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

                    await new Promise(resolve => setTimeout(resolve, 4000));

                    await goto('/orders');
                }
            );
        }

        Info.set('All the orders have been sent.');

        console.log('---- buyNow end ----');
    }

    onMount(async () => {
        for (const stall of $ShoppingCart.products.values()) {
            for (const product of stall.values()) {
                let merchantPublicKey = product.merchantPubkey;

                if (!merchantPubkeys.includes(merchantPublicKey)) {
                    merchantPubkeys.push(merchantPublicKey);
                }
            }
        }

        // refreshStalls($NostrPool);

        getStalls($NostrPool, merchantPubkeys,
            (stallEvent) => {
                let content = JSON.parse(stallEvent.content)
                content.createdAt = stallEvent.created_at;
                content.merchantPubkey = stallEvent.pubkey;

                if (!content.id) {
                    let stallId = getFirstTagValue(stallEvent.tags, 'd');
                    if (stallId !== null) {
                        content.id = stallId;
                    } else {
                        return;
                    }
                }

                let stallId = content.id;

                if (stallId in stalls) {
                    if (stalls[stallId].createdAt < stallEvent.created_at) {
                        stalls[stallId] = content;
                    }
                } else {
                    stalls[stallId] = content;
                }
            });
    });
</script>

<svelte:head>
    <title>Checkout</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-12 lg:mb-12 p-4">Checkout</h1>

{#if $ShoppingCart.summary.numProducts}
    <div class="flex flex-col w-full lg:flex-row px-12">
        <div class="grid flex-grow card bg-base-300 rounded-box place-items-center p-8 w-full lg:w-2/4">
            <h2 class="card-title">Shipping information</h2>
            <p>If you're purchasing a physical product, include all the info required so the merchant can send you the products.</p>

            <div class="form-control w-full max-w-xs mt-6">
                <label class="label">
                    <span class="label-text">Name</span>
                </label>
                <input bind:value={name} type="text" class="input input-bordered input-warning w-full max-w-xs" />
            </div>

            <div class="form-control w-full max-w-xs">
                <label class="label">
                    <span class="label-text">Shipping address</span>
                </label>
                <input bind:value={address} type="text" class="input input-bordered input-warning w-full max-w-xs" />
                <label class="label">
                    <span class="label-text-alt">Full shipping address including country, etc.</span>
                </label>
            </div>

            <div class="form-control w-full max-w-xs">
                <label class="label">
                    <span class="label-text">Message for the seller</span>
                </label>
                <textarea bind:value={message} class="textarea textarea-bordered input-warning" placeholder="Optional"></textarea>
            </div>
        </div>

        <div class="divider lg:divider-horizontal"></div>

        <div class="grid gap-5 flex-grow card bg-base-300 rounded-box place-items-center p-8 w-full lg:w-2/4">
            <h2 class="card-title">Contact information</h2>
            <p>Nostr private messages is the default contact method, but you could also provide email or phone contact information if you prefer that way.</p>

            <div class="grid gap-5">
                <div class="form-control">
                    <label class="input-group input-group-lg">
                        <span>
                            <div class="w-9 h-9"><Nostr /></div>
                        </span>
                        <input bind:value={nostrPublicKey} type="text" class="input input-bordered input-warning w-full max-w-lg" />
                    </label>
                </div>
                <div class="form-control">
                    <label class="input-group input-group-lg">
                        <span>
                            <div class="w-9 h-9"><Email /></div>
                        </span>
                        <input bind:value={email} type="text" class="input input-bordered input-warning w-full max-w-lg" />
                    </label>
                </div>
                <div class="form-control">
                    <label class="input-group input-group-lg">
                        <span>
                            <div class="w-9 h-9"><Phone /></div>
                        </span>
                        <input bind:value={phone} type="text" class="input input-bordered input-warning w-full max-w-lg" />
                    </label>
                </div>
            </div>
        </div>
    </div>

    <div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">
        <span class="font-bold text-lg mt-10">You're ordering {$ShoppingCart.summary.totalQuantity} products from {$ShoppingCart.summary.stalls} merchants. Check and choose the shipping options for each one of them:</span>

        <table class="table table-auto w-full place-content-center">
            <thead>
                <tr class="text-center">
                    <th>Name</th>
                    <th>Image</th>
                    <th>Total</th>
                </tr>
            </thead>

            <tbody>
            {#each [...$ShoppingCart.products] as [stallId, products], i}
                <tr>
                    <td colspan="3" class="bg-gray-700"><p class="ml-3">
                        {#if stalls[stallId] && stalls[stallId].name}
                            Order {i+1}: {stalls[stallId].name}
                        {:else}
                            Order {i+1}
                        {/if}
                    </p></td>
                </tr>
                <tr>
                    <td colspan="3" class="bg-gray-700 ml-4">
                        {#if stalls[stallId] && stalls[stallId].shipping}
                            <p class="ml-3">Shipping:
                                <select bind:value={stalls[stallId].shippingOption} class="select select-primary w-full max-w-lg ml-1">
                                    {#if stalls[stallId].shipping.length > 1}
                                        <option disabled selected value="0">Choose a shipping option:</option>
                                    {/if}

                                    {#each stalls[stallId].shipping as shippingOption}
                                        <option value="{shippingOption.id}">
                                            {shippingOption.name} -
                                            {#if shippingOption.countries}
                                                {#if !(shippingOption.countries.length === 1 && shippingOption.countries[0] === shippingOption.name)}
                                                    ({shippingOption.countries.join(', ')}) -
                                                {/if}
                                            {/if}
                                            {shippingOption.cost} {shippingOption.currency}
                                        </option>
                                    {/each}
                                </select>
                            </p>
                        {:else}
                            Loading shipping options...
                        {/if}
                    </td>
                </tr>

                {#each [...products] as [productId, product]}
                    <tr class="text-center">
                        <td>{#if product.name}{product.name}{/if}</td>
                        <td>
                            <div class="card bg-base-100 shadow-xl w-full lg:w-32">
                                <figure><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
                            </div>
                        </td>
                        <td>{product.price} x {product.orderQuantity} = <div></div><div>{(product.orderQuantity ?? 0) * product.price} {#if product.currency}{product.currency}{/if}</div></td>
                    </tr>
                {/each}
            {/each}
            </tbody>
        </table>

        <div class="card-actions justify-center">
            <a class="btn btn-primary" on:click|preventDefault={buyNow}>Buy now</a>
        </div>
    </div>

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
