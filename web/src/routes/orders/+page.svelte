<script>
    import {NostrPool, stalls} from "$lib/stores";
    import {onMount} from "svelte";
    import {getPrivateMessages} from "$lib/services/nostr.ts";
    import {formatTimestamp} from "$lib/nostr/utils.ts";
    import {decode} from "light-bolt11-decoder";
    import QRLocal from "$lib/components/QRLocal.svelte";
    import {refreshStalls} from "$lib/shopping.ts";

    let paymentModalVisible = false;
    let paymentLink = null;
    let paymentProtocol = null;
    let waitingForStallReply = false;

    let orders = [];
    let sortedOrders = [];

    $: {
        for (const [orderId, order] of Object.entries(orders)) {
            if (order.type === 0) {
                waitingForStallReply = true;
                break;
            }
        }

        sortedOrders = Object.entries(orders).sort((a, b) => {
                return b[1].created_at - a[1].created_at;
        });
    }

    onMount(async () => {
        await getPrivateMessages($NostrPool,
            (privateMessage) => {
                if (privateMessage !== null) {
                    //console.log('----------------------------> PM (1):', typeof privateMessage);

                    if (typeof privateMessage === 'object') {
                        // console.log('----------------------------> PM (2):', privateMessage);

                        let orderId = privateMessage.id;

                        let type;

                        if (privateMessage.type) {
                            type = Number(privateMessage.type);
                        } else {
                            // Workaround until NostrMarket adds the "type" property
                            if (privateMessage.payment_options) {
                                type = 1;
                            } else if (privateMessage.paid) {
                                type = 2;
                            } else {
                                type = 0;
                            }
                        }

                        if (type === 1) {
                            for (const paymentOption of privateMessage.payment_options) {
                                if (paymentOption.type === 'ln') {
                                    const decodedInvoice = decode(paymentOption.link);

                                    paymentOption.amount =
                                        decodedInvoice.sections.filter((section) => {
                                            return section.name === 'amount'
                                        })[0].value / 1000;

                                    paymentOption.expiry = decodedInvoice.expiry;
                                }
                            }
                        }

                        // <small>Expires in {decode(payment_option.link).expiry / 60} minutes</small>

                        if (orderId in orders) {
                            // Because some properties are the same in different types
                            // like "message"
                            if (privateMessage.created_at > orders[orderId].created_at) {
                                orders[orderId] = {...orders[orderId], ...privateMessage};
                            } else {
                                orders[orderId] = {...privateMessage, ...orders[orderId]};
                            }

                            orders[orderId].type = type;

                        } else {
                            orders[orderId] = privateMessage;

                            if (!privateMessage.type) {
                                orders[orderId].type = type;
                            }
                        }
                    }
                }
            });

        refreshStalls($NostrPool);
    });
</script>

<svelte:head>
    <title>Orders</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-12 lg:mb-12 p-4">Orders</h1>

{#if Object.keys(orders).length > 0}
    <div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">

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
                    <tr>
                        <td class="">
                            <p class="ml-3">
                                {#if $stalls !== null && $stalls.stalls[order.stall_id]}
                                    {$stalls.stalls[order.stall_id].name ?? ''} /
                                {/if}
                                {orderId}
                            </p>
                            <small class="ml-3">
                                {#if order.items}
                                    {#each order.items as item}
                                        #{item.product_id} - {item.quantity} units
                                    {/each}
                                {/if}
                            </small>
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
                                                    <button class="btn gap-2" on:click|preventDefault={() => {paymentLink = payment_option.link; paymentProtocol = 'lightning'; paymentModalVisible = true}}>
                                                        ⚡ Pay with Lightning
                                                    </button>
                                                </p>
                                                <small>Expires in {payment_option.expiry / 60} minutes</small>
                                            {:else}
                                                <small>⚡ Lightning Invoice expired</small>
                                            {/if}
                                        {:else}
                                            <p>
                                                <button class="btn gap-2" on:click|preventDefault={() => {paymentLink = payment_option.link; paymentProtocol = 'bitcoin'; paymentModalVisible = true}}>
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
                                {#if !['Payment received.'].includes(order.message)}
                                    <p>
                                        🛈 {order.message}
                                    </p>
                                {/if}
                            {:else}
                                <p>Unknown</p>
                            {/if}
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
{:else}
    <div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">
        <div class="p-6 text-lg">
            <p>You don't have any order yet.</p>
            <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stalls</a> and buy some products.</p>
        </div>
    </div>
{/if}

<!-- Nostr text confirmation Modal -->
<input type="checkbox" id="nostrTextConfirmation" class="modal-toggle" bind:checked={paymentModalVisible}/>
<div class="modal">
    <div class="modal-box relative">
        <label for="nostrTextConfirmation" class="btn btn-sm btn-circle absolute right-2 top-2">✕</label>
        <h3 class="text-lg font-bold">Pay your order:</h3>

        {#if paymentLink}
            <QRLocal address="{paymentLink}" protocol="{paymentProtocol}" />
        {:else}
            <p>Error: payment address not available</p>
        {/if}
    </div>
</div>
