<script>
    import {NostrPublicKey, privateMessages, products, stalls} from "$lib/stores";
    import {formatTimestamp} from "$lib/nostr/utils.ts";
    import QRLocal from "$lib/components/QRLocal.svelte";
    import {refreshProducts, refreshStalls} from "$lib/shopping.ts";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {requestLoginModal} from "$lib/utils.ts";
    import {onDestroy} from "svelte";

    let paymentModalVisible = false;
    let paymentLink = null;
    let paymentProtocol = null;

    let sortedOrders = [];
    let ordersToBePaidNow = [];

    let hideOldOrders = true;
    const oldOrderTime = 7776000000;  // 3 months

    let showAutomaticPayments = false;

    $: {
        sortedOrders = Object.entries($privateMessages.automatic).sort((a, b) => {
            return b[1].created_at - a[1].created_at;
        });

        ordersToBePaidNow = Object.fromEntries( Object.entries($privateMessages.automatic).filter(([orderId, order]) => {
            if (order.type === 1) {
                if (order.payment_options) {
                    for (const payment_option of order.payment_options) {
                        if (payment_option.type === 'ln') {
                            if (Date.now() < ((order.created_at * 1000) + (payment_option.expiry * 1000))) {
                                return true;
                            }
                        } else {
                            return true;
                        }
                    }
                }
            }

            return false;
        }));
    }

    $: if (showAutomaticPayments && Object.entries(ordersToBePaidNow).length > 0) {
        let orderToPay = Object.entries(ordersToBePaidNow)[0][1];

        let link;
        let protocol;

        if (orderToPay.payment_options) {
            for (const payment_option of orderToPay.payment_options) {
                if (payment_option.type === 'ln') {
                    if (Date.now() > ((orderToPay.created_at * 1000) + (payment_option.expiry * 1000))) {
                        protocol = 'lightning';
                        link = payment_option.link;
                    }
                } else {
                    protocol = 'bitcoin';
                    link = payment_option.link;
                }
            }
        }

        payOrder(link, protocol, orderToPay);
    } else {
        paymentModalVisible = false;
    }

    export function payOrder(link, protocol, payment = null) {
        paymentLink = link;
        paymentProtocol = protocol;

        if (payment) {

        }

        paymentModalVisible = true;
    }

    const nostrPublicKeyUnsubscribe = NostrPublicKey.subscribe(async nostrPublicKeyValue => {
        if (nostrPublicKeyValue) {
            refreshStalls();
            refreshProducts();

            await new Promise(resolve => setTimeout(resolve, 2500));
            showAutomaticPayments = true;
        } else {
            requestLoginModal();
        }
    });
    onDestroy(nostrPublicKeyUnsubscribe);
</script>

<svelte:head>
    <title>Orders</title>
</svelte:head>

<Titleh1>Orders</Titleh1>

{#if Object.keys($privateMessages.automatic).length > 0}
    <div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-16 place-content-center">
        {#if Object.entries(ordersToBePaidNow).length > 0}
            <div class="alert alert-warning shadow-lg">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    <span>
                    You still have to pay <b>{Object.entries(ordersToBePaidNow).length}</b> of your orders!
                    <ul class="list-disc list-inside ml-8">
                        {#each Object.entries(ordersToBePaidNow) as [orderId, order]}
                            <li>{order.id}</li>
                        {/each}
                    </ul>
                </span>

                </div>
            </div>
        {/if}

        <div class="text-right mb-4">
            Hide old orders (> 3 months)
            <input type="checkbox" bind:checked={hideOldOrders} class="checkbox checkbox-md mr-3" class:checkbox-success={hideOldOrders} />
        </div>

        <table class="table table-auto w-full place-content-center">
            <thead>
            <tr class="text-center">
                <th>Order</th>
                <th>Last update</th>
                <th>Status</th>
            </tr>
            </thead>
            <tbody>
            {#each sortedOrders as [orderId, order]}
                {#if !hideOldOrders || (hideOldOrders && (Date.now() < ((order.created_at * 1000) + oldOrderTime)))}
                    <tr>
                        <td>
                            <p class="ml-3">
                                Order # - {orderId}
                            </p>

                            {#if $stalls !== null && $stalls.stalls[order.stall_id]}
                                <p class="ml-3">
                                    Stall: {$stalls.stalls[order.stall_id].name ?? ''}
                                </p>
                            {/if}

                            {#if order.items}
                                <ul class="list-disc list-inside ml-8">
                                    {#each order.items as item}
                                        <li>
                                            <small>
                                                {#if $products !== null && $products.products[item.product_id]}
                                                    {$products.products[item.product_id].name}
                                                {:else}
                                                    #{item.product_id}
                                                {/if}
                                                - {item.quantity} units
                                            </small>
                                        </li>
                                    {/each}
                                </ul>
                            {/if}
                        </td>
                        <td class="text-center">
                            {formatTimestamp(order.created_at)}
                        </td>
                        <td class="text-center">
                            {#if order.type === 0}
                                <p>Waiting for reply from the store</p>
                            {:else if order.type === 1}
                                {#if order.payment_options}
                                    {#each order.payment_options as payment_option}
                                        {#if payment_option.type === 'ln'}
                                            <p>
                                                {payment_option.amount} sats
                                            </p>

                                            {#if Date.now() < ((order.created_at * 1000) + (payment_option.expiry * 1000)) }
                                                <p>
                                                    Waiting for payment
                                                    <button class="btn gap-2" on:click|preventDefault={() => {payOrder(payment_option.link, 'lightning')}}>
                                                        ⚡ Pay with Lightning
                                                    </button>
                                                </p>
                                                <small>Expires in {payment_option.expiry / 60} minutes</small>
                                            {:else}
                                                <small>⚡ Lightning Invoice expired</small>
                                            {/if}
                                        {:else}
                                            <p>
                                                <button class="btn gap-2" on:click|preventDefault={() => {payOrder(payment_option.link, 'bitcoin')}}>
                                                    Pay with Bitcoin
                                                </button>
                                            </p>
                                        {/if}
                                    {/each}
                                {/if}
                            {:else if order.type === 2}
                                <p>
                                    {#if order.payment_options}
                                        {#each order.payment_options as payment_option}
                                            {#if payment_option.type === 'ln'}
                                                <p>
                                                    {payment_option.amount} sats
                                                </p>
                                            {/if}
                                        {/each}
                                    {/if}
                                    {#if order.paid}
                                        ✅ Payment received
                                    {:else}
                                        ❌ Payment not received
                                    {/if}
                                </p>
                                <p>
                                    {#if order.shipped}
                                        ✅ Order shipped
                                    {:else}
                                        ❌ Order not shipped yet
                                    {/if}
                                </p>
                            {:else}
                                <p>Unknown</p>
                            {/if}

                            {#if order.message && order.type !== 0 && !['Payment received.'].includes(order.message)}
                                <p>
                                    🛈 {order.message}
                                </p>
                            {/if}
                        </td>
                    </tr>
                {/if}
            {/each}
            </tbody>
        </table>
    </div>
{:else}
    <div class="grid justify-center items-center lg:mx-20 place-content-center p-6 text-lg">
        <p>You don't have any order yet.</p>
        <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stalls</a> and buy some products.</p>
    </div>
{/if}

<!-- Nostr text confirmation Modal -->
<input type="checkbox" id="nostrTextConfirmation" class="modal-toggle" bind:checked={paymentModalVisible} on:change={() => showAutomaticPayments = false}/>
<div class="modal">
    <div class="modal-box relative">
        <label for="nostrTextConfirmation" class="btn btn-sm btn-circle absolute right-2 top-2">✕</label>

        {#if Object.entries(ordersToBePaidNow).length > 0}
            <div>
                You have to pay {Object.entries(ordersToBePaidNow).length} orders. Start by paying this one:
            </div>
        {/if}

        <h3 class="text-lg font-bold">Pay your order:</h3>

        {#if paymentLink}
            <QRLocal address="{paymentLink}" protocol="{paymentProtocol}" />
        {:else}
            <p>Error: payment address not available</p>
        {/if}
    </div>
</div>
