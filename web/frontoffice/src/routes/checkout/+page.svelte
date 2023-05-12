<script>
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Email from "$sharedLib/components/icons/Email.svelte";
    import Phone from "$sharedLib/components/icons/Phone.svelte";
    import Nostr from "$sharedLib/components/icons/Nostr.svelte";
    import {Error, Info, NostrPool, NostrPublicKey, ShoppingCart, stalls} from "$lib/stores";
    import {onImgError, refreshStalls} from "$lib/shopping";
    import {onMount} from "svelte";
    import { v4 as uuidv4 } from "uuid";
    import {sendPrivateMessage, getPrivateMessages, checkExtensionOrShowDialog} from "$lib/services/nostr";
    import {goto} from "$app/navigation";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";

    let name = null;
    let address = null;
    let message = null;

    let phone = null;
    let email = null;

    export async function buyNow() {
        console.log('---- buyNow start ----');

        if (!checkExtensionOrShowDialog()) {
            return;
        }

        if (!$NostrPublicKey) {
            Error.set('You need to use a Nostr extension and login with it.');
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
            console.log('************ jsonOrder:  ', order);

            sendPrivateMessage($NostrPool, $stalls.stalls[stallId].merchantPubkey, messageOrder,
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
        }

        Info.set('All the orders have been sent.');

        console.log('---- buyNow end ----');
    }

    onMount(async () => {
        if (checkExtensionOrShowDialog()) {
            if (!$NostrPublicKey) {
                $NostrPublicKey = await window.nostr.getPublicKey();
            }

            refreshStalls($NostrPool);

            // Pre-fill contact data with info from old orders
            await getPrivateMessages($NostrPool, $NostrPublicKey,
                (privateMessage) => {
                    if (privateMessage !== null && typeof privateMessage === 'object') {
                        if (!privateMessage.paid) {     // So it's type === 1, but NostrMarket is not sending the type yet
                            if (privateMessage.name) {
                                name = privateMessage.name;
                            }
                            if (privateMessage.address) {
                                address = privateMessage.address;
                            }

                            if (privateMessage.contact?.phone) {
                                phone = privateMessage.contact.phone;
                            }
                            if (privateMessage.contact?.email) {
                                email = privateMessage.contact.email;
                            }
                        }
                    }
                });
        }
    });
</script>

<svelte:head>
    <title>Checkout</title>
</svelte:head>

<Titleh1>Checkout</Titleh1>

{#if $ShoppingCart.summary.numProducts}
    <div class="flex flex-col md:flex-row w-full md:px-12">
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
                        <input bind:value={$NostrPublicKey} type="text" class="input input-bordered input-warning w-full max-w-lg" />
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



    <div class="md:grid justify-center mt-10 mb-10">
        <table class="w-fit md:w-full rounded-md">
            <thead>
                <tr class="bg-gray-700 text-center">
                    <th>Name</th>
                    <th>Image</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody class="text-base">
                {#each [...$ShoppingCart.products] as [stallId, products], i}
                    <tr>
                        <td colspan="3" class="bg-gray-700/60">
                            <p class="mx-3">
                                Order #{i+1}
                            </p>
                            {#if $stalls.stalls[stallId] && $stalls.stalls[stallId].name}
                                <p class="mx-3 mt-3">
                                    {$stalls.stalls[stallId].name}
                                </p>
                            {/if}

                            <p class="mx-3 mt-3">
                                {#if $stalls.stalls[stallId] && $stalls.stalls[stallId].shipping}
                                    Shipping:
                                    <select bind:value={$stalls.stalls[stallId].shippingOption} class="select select-sm select-primary max-w-lg ml-1">
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

                    {#each [...products] as [productId, product]}
                        <tr class="text-center">
                            <td>
                                <p class="px-1">{#if product.name}{product.name}{/if}</p>
                            </td>
                            <td>
                                <div class="card bg-base-100 shadow-xl w-24 md:w-32">
                                    <figure><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
                                </div>
                            </td>
                            <td>
                                <p class="px-1">
                                    {product.price} x {product.orderQuantity} = {(product.orderQuantity ?? 0) * product.price} {#if product.currency}{product.currency}{/if}
                                </p>
                            </td>
                        </tr>
                    {/each}
                {/each}
            </tbody>
        </table>

        <!-- Mobile -->
        <!--
        <table class="w-fit rounded-md md:hidden text-sm text-left">
            <thead>
            <tr class="text-center">
                <th>Name</th>
                <th>Image</th>
                <th>Total</th>
            </tr>
            </thead>

            <tbody class="text-xs">
                {#each [...$ShoppingCart.products] as [stallId, products], i}
                    <tr>
                        <td colspan="3" class="bg-gray-700">
                            <p class="ml-3">
                                {#if $stalls.stalls[stallId] && $stalls.stalls[stallId].name}
                                    Order {i+1}: {$stalls.stalls[stallId].name}
                                {:else}
                                    Order {i+1}
                                {/if}
                            </p>

                            <p class="ml-3 mt-3">
                                {#if $stalls.stalls[stallId] && $stalls.stalls[stallId].shipping}
                                    Shipping:
                                    <select bind:value={$stalls.stalls[stallId].shippingOption} class="select select-sm select-primary max-w-lg ml-1">
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

                    {#each [...products] as [productId, product]}
                        <tr class="text-center">
                            <td>{#if product.name}{product.name}{/if}</td>
                            <td>
                                <div class="card bg-base-100 shadow-xl w-28 md:w-32">
                                    <figure><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
                                </div>
                            </td>
                            <td>{product.price} x {product.orderQuantity} = <div></div><div>{(product.orderQuantity ?? 0) * product.price} {#if product.currency}{product.currency}{/if}</div></td>
                        </tr>
                    {/each}
                {/each}
            </tbody>
        </table>-->

        <div class="card-actions justify-center mt-16">
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
