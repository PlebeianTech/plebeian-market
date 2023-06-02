<script>
    import {NostrPublicKey, privateMessages, products, stalls} from "$lib/stores";
    import {formatTimestamp} from "$lib/nostr/utils.ts";
    import QRLocal from "$lib/components/QRLocal.svelte";
    import {refreshProducts, refreshStalls} from "$lib/shopping.ts";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import Bitcoin from "$sharedLib/components/icons/Bitcoin.svelte";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
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

    $: paidPaymentsStorage = [];

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

        if (orderToPay.payment_options) {
            for (const payment_option of orderToPay.payment_options) {
                if (payment_option.type === 'ln') {
                    if (Date.now() > ((orderToPay.created_at * 1000) + (payment_option.expiry * 1000))) {
                        showPaymentDetails(orderToPay.id, payment_option.link, payment_option.amount_sats, payment_option.type, orderToPay);
                    }
                } else {
                    showPaymentDetails(orderToPay.id, payment_option.link, payment_option.amount_sats, payment_option.type, orderToPay);
                }
            }
        }

    } else {
        paymentModalVisible = false;
    }

    function bech32Encode(url) {
        let words = bech32.toWords(BufferPolyfill.from(url, 'utf8'))
        return bech32.encode('lnurl', words, 1500)
    }

    function showPaymentDetails(orderId, data, amount, type, payment = null) {
        if (type === 'ln') {
            paymentInfo = {
                link: data,
                protocol: 'lightning',
                amount: amount,
                orderId: orderId
            }
        } else if (type === 'lnurl') {
            let lnAddressArray = data.split("@");
            let name = lnAddressArray[0];
            let domain = lnAddressArray[1];

            let link = 'https://' + domain + '/.well-known/lnurlp/' + name;

            paymentInfo = {
                link: bech32Encode(link).toUpperCase(),
                protocol: 'lightning',
                amount: amount,
                orderId: orderId
            }
        } else if (type === 'btc') {
            let btcLink = data;

            if (amount !== null || orderId !== null) {
                btcLink += '?';
            }
            if (amount !== null) {
                btcLink += 'amount=' + Number(amount / 100000000).toFixed(8);
            }
            if (orderId) {
                if (btcLink.includes('amount')) {
                    btcLink += '&';
                }
                btcLink += 'message=Order#' + orderId;
            }

            paymentInfo = {
                link: btcLink,
                protocol: 'bitcoin',
                amount: amount,
                orderId: orderId
            }
        } else {
            alert('Payment type not supported: ' + type);
        }

        paymentModalVisible = true;
    }

    const nostrPublicKeyUnsubscribe = NostrPublicKey.subscribe(async nostrPublicKeyValue => {
        if (nostrPublicKeyValue) {
            refreshStalls();
            refreshProducts();

//            await new Promise(resolve => setTimeout(resolve, 2500));
//            showAutomaticPayments = true;
        } else {
            requestLoginModal();
        }
    });
    onDestroy(nostrPublicKeyUnsubscribe);

    function getPaidPaymentsFromStorage() {
        let paidPaymentsStorageJson = localStorage.getItem('paidPayments');
        paidPaymentsStorage = JSON.parse(paidPaymentsStorageJson) ?? [];
    }

    function markPaymentAsPaid(paymentId) {
        if (!paidPaymentsStorage.includes(paymentId)) {
            paidPaymentsStorage[paidPaymentsStorage.length] = paymentId;
            localStorage.setItem('paidPayments', JSON.stringify(paidPaymentsStorage));
        }

        paymentConfirmationModalVisible = false
        paymentModalVisible = false;
    }

    onMount(async () => {
        getPaidPaymentsFromStorage();
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

                                        {#if paidPaymentsStorage.includes(orderId) }
                                            <div class="flex flex-col justify-center items-center">
                                                <span class="w-10 h-10 mb-1"><Clock /></span>
                                                <p class="hidden md:block">Market as paid.<br>Waiting for payment confirmation from the seller...</p>
                                                <p class="md:hidden">Waiting confirmation from seller...</p>
                                            </div>
                                        {:else}
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
                                                            <button class="btn btn-outline gap-2 mb-4 md:mb-2" on:click|preventDefault={() => {showPaymentDetails(orderId, payment_option.link, null, payment_option.type)}}>
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
                                                        <button class="btn btn-outline gap-2 mb-4 md:mb-2" on:click|preventDefault={() => {showPaymentDetails(orderId, payment_option.link, payment_option.amount_sats, payment_option.type)}}>
                                                            <p class="text-2xl">⚡</p> Show payment QR
                                                        </button>
                                                    </p>
                                                {:else if payment_option.type === 'btc'}
                                                    <!-- BTC ONCHAIN -->
                                                    <p>
                                                        <button class="btn btn-outline gap-2 mb-4 md:mb-2" on:click|preventDefault={() => {showPaymentDetails(orderId, payment_option.link, payment_option.amount_sats, payment_option.type)}}>
                                                            <span class="h-7 w-7" ><Bitcoin /></span> Pay with Bitcoin
                                                        </button>
                                                    </p>
                                                {:else if payment_option.type === 'url'}
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

                                            {#if order.message && !['Payment received.'].includes(order.message)}
                                                <p>
                                                    🛈 {order.message}
                                                </p>
                                            {/if}
                                        {/if}
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

                                    {#if order.message && !['Payment received.'].includes(order.message)}
                                        <p>
                                            🛈 {order.message}
                                        </p>
                                    {/if}
                                {:else}
                                    <p>Unknown</p>
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
            <div class="py-4 md:p-6 bg-white">
                <QRLocal {paymentInfo} />

                {#if paymentInfo.protocol === 'lightning'}
                    <div class="mt-4 md:mt-6 pb-0 flex flex-col justify-center items-center">
                        <div class="block justify-center items-center mx-auto mb-4">
                            <button class="btn btn-success" on:click|preventDefault={() => paymentConfirmationModalVisible = true}>Mark as paid</button>
                        </div>

                        <ul class="list-disc list-outside text-xs md:text-sm">
                            {#if paymentInfo.amount}
                                <li class="mb-3">You must send <b>{paymentInfo.amount} sats</b> to the seller</li>
                            {/if}
                            <li class="mb-3">If your wallet let you specify a <b>comment</b> while paying, put <b>{paymentInfo.orderId.slice(-5)}</b></li>
                            <li class="mb-3 md:hidden">You can <b>tap the QR code</b> to open your Lightning wallet.</li>
                            <li class="mb-3 md:mb-0">Mark the payment as <b>paid</b> using the green button when you're done.</li>
                            <li>As the <b>payment goes directly to the seller</b> and <b>Lightning payments are private</b>,
                                we cannot tell you if the payment was successful. You must rely on your own wallet for this.</li>
                        </ul>
                    </div>
                {/if}
            </div>

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
            Payment completed successfully?
        </h3>

        <p class="p-6 md:p-10 text-justify">Have you got a confirmation from your wallet that this payment has completed successfully?</p>

        <div class="flex justify-center items-center">
            <button class="btn btn-error mr-6" on:click|preventDefault={() => paymentConfirmationModalVisible = false}>Not yet</button>
            <button class="btn btn-success" on:click|preventDefault={() => markPaymentAsPaid(paymentInfo.orderId)}>Yes, payment correct</button>
        </div>
    </div>
</div>
