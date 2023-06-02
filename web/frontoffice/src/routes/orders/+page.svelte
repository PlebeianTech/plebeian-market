<script>
    import {NostrPublicKey, privateMessages, products, stalls} from "$lib/stores";
    import {formatTimestamp} from "$lib/nostr/utils.ts";
    import QRLocal from "$lib/components/QRLocal.svelte";
    import {refreshProducts, refreshStalls} from "$lib/shopping.ts";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import Bitcoin from "$sharedLib/components/icons/Bitcoin.svelte";
    import {requestLoginModal} from "$lib/utils.ts";
    import {onDestroy, onMount} from "svelte";
    import {bech32} from "bech32";
    import {Buffer as BufferPolyfill} from "buffer";

    let paymentModalVisible = false;
    let paymentConfirmationModalVisible = false;

    let paymentInfo = {
        link: null,
        protocol: null,
        amount: null,
        orderId: null
    };

    let sortedOrders = [];
    let ordersToBePaidNow = [];

    let hideOldOrders = true;
    const oldOrderTime = 7776000000;  // 3 months

    let showAutomaticPayments = false;

    $: {
        sortedOrders = Object.entries($privateMessages.automatic).sort((a, b) => {
            return b[1].created_at - a[1].created_at;
        });

        ordersToBePaidNow = Object.fromEntries( Object.entries($privateMessages.automatic).filter(([, order]) => {
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

        showPaymentDetails(orderToPay.id, link, protocol, orderToPay);
    } else {
        paymentModalVisible = false;
    }

    function bech32Encode(url) {
        let words = bech32.toWords(BufferPolyfill.from(url, 'utf8'))
        return bech32.encode('lnurl', words, 1500)
    }

    function showPaymentDetails(orderId, data, amount, protocol, payment = null) {
        if (protocol === 'ln') {
            paymentInfo = {
                link: data,
                protocol: 'lightning',
                amount: amount,
                orderId: orderId.slice(-5)
            }
        } else if (protocol === 'lnurl') {
            let lnAddressArray = data.split("@");
            let name = lnAddressArray[0];
            let domain = lnAddressArray[1];

            //let link = 'https://' + domain + '/.well-known/lnurlp/' + name + '?amount=' + amount*1000;
            let link = 'https://' + domain + '/.well-known/lnurlp/' + name;

            paymentInfo = {
                link: bech32Encode(link).toUpperCase(),
                protocol: 'lightning',
                amount: amount,
                orderId: orderId.slice(-5)
            }
        } else if (protocol === 'btc') {
            paymentInfo = {
                link: data,
                protocol: protocol,
                amount: amount,
                orderId: orderId.slice(-5)
            }
        } else {
            alert('Payment type not supported.')
        }

        if (payment) {

        }

        paymentModalVisible = true;
    }

    const nostrPublicKeyUnsubscribe = NostrPublicKey.subscribe(async nostrPublicKeyValue => {
        if (nostrPublicKeyValue) {
            refreshStalls();
            refreshProducts();

            await new Promise(resolve => setTimeout(resolve, 2500));
//            showAutomaticPayments = true;
        } else {
            requestLoginModal();
        }
    });
    onDestroy(nostrPublicKeyUnsubscribe);

    function getPaidPayments() {
        let paidPaymentsStorageJson = localStorage.getItem('paidPayments');
        return JSON.parse(paidPaymentsStorageJson) ?? {};
    }

    function markPaymentAsPaid(paymentId) {
        let paidPayments = getPaidPayments();
        console.log('paidPayments before', paidPayments);
        paidPayments.push(paymentId);
        console.log('paidPayments after', paidPayments);
        //localStorage.setItem('paidPayments', JSON.stringify(messages));
    }

    onMount(async () => {

    });
</script>

<svelte:head>
    <title>Orders</title>
</svelte:head>

<Titleh1>Orders</Titleh1>

<div class="md:grid justify-center mt-0 md:mt-10 mb-10">
    {#if Object.keys($privateMessages.automatic).length > 0}
        <div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-10 place-content-center">
            {#if Object.entries(ordersToBePaidNow).length > 0}
                <div class="alert alert-warning shadow-lg">
                    <div>
                        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        <div>
                            <p class="mb-1">You still have to pay <b>{Object.entries(ordersToBePaidNow).length}</b> of your orders!</p>
                            <ul class="list-disc list-inside ml-3 md:ml-5 text-xs md:text-sm">
                                {#each Object.entries(ordersToBePaidNow) as [orderId, order]}
                                    <li>{order.id}</li>
                                {/each}
                            </ul>
                        </div>
                    </div>
                </div>
            {/if}

            <div class="text-right md:mb-3">
                Hide old orders (> 3 months)
                <input type="checkbox" bind:checked={hideOldOrders} class="checkbox checkbox-md mr-3" class:checkbox-success={hideOldOrders} />
            </div>

            <table class="block w-full rounded border border-gray-400 p-2 md:p-4">
                <thead>
                    <tr class="text-center">
                        <th class="text-left">Order</th>
                        <th>Last update</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                {#each sortedOrders as [orderId, order]}
                    {#if !hideOldOrders || (hideOldOrders && (Date.now() < ((order.created_at * 1000) + oldOrderTime)))}
                        <tr class="border-y border-gray-600 hover">
                            <td>
                                <p class="text-sm md:hidden">
                                    # {orderId.substring(0,8)}...
                                </p>
                                <p class="text-sm hidden md:block">
                                    # {orderId}
                                </p>

                                {#if $stalls !== null && $stalls.stalls[order.stall_id]}
                                    <p class="mt-2">
                                        <b>Stall</b>: {$stalls.stalls[order.stall_id].name ?? ''}
                                    </p>
                                {/if}

                                {#if order.items}
                                    <ul class="list-disc list-inside ml-2">
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
                            <td class="text-center px-0 md:px-4">
                                {formatTimestamp(order.created_at)}
                            </td>
                            <td class="text-center">
                                {#if order.type === 0}
                                    <p>Waiting for reply from the store</p>
                                {:else if order.type === 1}
                                    {#if order.payment_options}

                                        {#each order.payment_options as payment_option}
                                            {#if payment_option.amount_sats || payment_option.amount}
                                                <p>
                                                    {payment_option.amount_sats ?? payment_option.amount} sats
                                                </p>
                                            {/if}

                                            {#if payment_option.type === 'ln'}
                                                <!-- LN INVOICES -->
                                                {#if Date.now() < ((order.created_at * 1000) + (payment_option.expiry * 1000)) }
                                                    <p>
                                                        Waiting for payment
                                                        <button class="btn btn-outline gap-2 mb-4 md:mb-2" on:click|preventDefault={() => {showPaymentDetails(orderId, payment_option.link, null, 'lightning')}}>
                                                            <p class="text-2xl">⚡</p> Show payment QR
                                                        </button>
                                                    </p>
                                                    <small>Expires in {payment_option.expiry / 60} minutes</small>
                                                {:else}
                                                    <small>⚡ Lightning Invoice expired</small>
                                                {/if}

                                            {:else if payment_option.type === 'lnurl'}
                                                <!-- LN ADDRESS -->
                                                <p>
                                                    <button class="btn btn-outline gap-2 mb-4 md:mb-2" on:click|preventDefault={() => {showPaymentDetails(orderId, payment_option.link, payment_option.amount_sats, 'lnurl')}}>
                                                        <p class="text-2xl">⚡</p> Show payment QR
                                                    </button>
                                                </p>
                                            {:else if payment_option.type === 'btc'}
                                                <!-- BTC ONCHAIN -->
                                                <p>
                                                    <button class="btn btn-outline gap-2 mb-4 md:mb-2" on:click|preventDefault={() => {showPaymentDetails(orderId, payment_option.link, payment_option.amount_sats, 'bitcoin')}}>
                                                        <span class="h-7 w-7" ><Bitcoin /></span> Pay with Bitcoin
                                                    </button>
                                                </p>
                                            {:else if payment_option.type === 'lnurl'}
                                                <!-- PAYMENT URL -->
                                                <p>
                                                    <button class="btn btn-outline gap-2 mb-4 md:mb-2" on:click|preventDefault={() => {window.open(payment_option.link, '_blank').focus()}}>
                                                        Open payment website
                                                    </button>
                                                </p>
                                            {:else}
                                                <p>
                                                    <button class="btn btn-disabled btn-outline gap-2 mb-4 md:mb-2" >
                                                        Unknown payment option
                                                    </button>
                                                </p>
                                            {/if}
                                        {/each}
                                    {/if}
                                {:else if order.type === 2}
                                    <p>
                                        {#if order.payment_options}
                                            <ul class="list-disc [&>*:first-child]:block">
                                                {#each  order.payment_options as payment_option}
                                                    {#if payment_option.amount_sats || payment_option.amount}
                                                        <li class="hidden">{payment_option.amount_sats ?? payment_option.amount} sats</li>
                                                    {/if}
                                                {/each}
                                            </ul>
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
</div>

<!-- QR payment modal -->
<input type="checkbox" id="nostrTextConfirmation" class="modal-toggle" bind:checked={paymentModalVisible} on:change={() => showAutomaticPayments = false}/>
<div class="modal">
    <div class="modal-box relative bg-white">
        <label for="nostrTextConfirmation" class="btn btn-sm btn-circle absolute right-2 top-2">✕</label>

        <h3 class="text-lg font-bold mb-0 text-black">
            {#if Object.entries(ordersToBePaidNow).length === 1}
                Pay your order:
            {:else if Object.entries(ordersToBePaidNow).length > 1}
                You have to pay {Object.entries(ordersToBePaidNow).length} orders. Start by paying this one:
            {/if}
        </h3>

        {#if paymentInfo.link}
            <QRLocal {paymentInfo} />
        {:else}
            <p>Error: payment address not available. Contact the seller.</p>
        {/if}
    </div>
</div>

<!-- Order paid confirmation -->
<input type="checkbox" id="paymentConfirmation" class="modal-toggle" bind:checked={paymentConfirmationModalVisible} on:change={() => showAutomaticPayments = false}/>
<div class="modal">
    <div class="modal-box relative bg-white">
        <label for="paymentConfirmation" class="btn btn-sm btn-circle absolute right-2 top-2">✕</label>

        <h3 class="text-lg font-bold mb-0 text-black">
            Has this payment been done successfully?
        </h3>

        <p>Did you scan this QR with your Lightning wallet and the result was OK?</p>

        <button class="btn btn-success">Yes, payment correct</button>
        <button class="btn btn-error">No, I got an error</button>
    </div>
</div>
