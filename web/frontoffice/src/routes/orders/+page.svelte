<script>
    import {products} from "$lib/stores";
    import {NostrPublicKey, stalls, privateMessages, Info} from "$sharedLib/stores";
    import {formatTimestamp, newNostrConversation} from "$sharedLib/nostr/utils";
    import QRLocal from "$lib/components/QRLocal.svelte";
    import {refreshProducts, refreshStalls} from "$lib/shopping";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import Bitcoin from "$sharedLib/components/icons/Bitcoin.svelte";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import {waitAndShowLoginIfNotLoggedAlready} from "$sharedLib/utils";
    import {onDestroy, onMount} from "svelte";
    import {bech32} from "bech32";
    import {Buffer as BufferPolyfill} from "buffer";
    import { afterNavigate } from "$app/navigation";
    import EmailIcon from "$sharedLib/components/icons/Email.svelte";

    let paymentModalVisible = false;
    let paymentConfirmationModalVisible = false;

    let paymentInfo = {
        link: null,
        protocol: null,
        amount: null
    };
    let orderToBePaid = null;
    let paymentOptionSelected = null;

    let sortedOrders = [];
    let ordersToBePaidNow = [];

    let hideOldOrders = true;
    const oldOrderTime = 7776000000;  // 3 months

    let showAutomaticPayments = false;

    $: paidPaymentsStorage = [];

    $: {
        sortedOrders = Object.entries($privateMessages.automatic)
            .filter(([, automaticMessage]) => {
                //return automaticMessage.type !== 10;
                return true;
            })
            .sort((a, b) => {
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
                        orderToBePaid = orderToPay;
                        showPaymentDetails();
                    }
                } else {
                    orderToBePaid = orderToPay;
                    showPaymentDetails();
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

    function getCurrentPaymentOptionInfo() {
        for (const option of orderToBePaid.payment_options) {
            if (option.type === paymentOptionSelected) {
                return option;
            }
        }
    }

    function getAmountToPay(order) {
        for (const option of order.payment_options) {
            if (option.amount_sats) {
                return option.amount_sats;
            }
        }
    }

    function showPaymentDetails() {
        if (!paymentOptionSelected) {
            // No payment option selected, pre-selecting the default one
            let paymentOptions = [];
            for (const payment_option of orderToBePaid.payment_options) {
                paymentOptions[paymentOptions.length] = payment_option.type;
            }

            if (paymentOptions.includes('ln')) {
                paymentOptionSelected = 'ln';
            } else if (paymentOptions.includes('lnurl')) {
                paymentOptionSelected = 'lnurl';
            } else if (paymentOptions.includes('btc')) {
                paymentOptionSelected = 'btc';
            }
        }

        let paymentOptionInfo = getCurrentPaymentOptionInfo();

        let orderId = orderToBePaid.id;
        let data = paymentOptionInfo.link;
        let amount = paymentOptionInfo.amount_sats;

        if (paymentOptionSelected === 'ln') {
            paymentInfo = {
                link: data,
                protocol: 'lightning',
                amount: amount,
            }
        } else if (paymentOptionSelected === 'lnurl') {
            let lnAddressArray = data.split("@");
            let name = lnAddressArray[0];
            let domain = lnAddressArray[1];

            let link = 'https://' + domain + '/.well-known/lnurlp/' + name;

            paymentInfo = {
                link: bech32Encode(link).toUpperCase(),
                protocol: 'lightning',
                amount: amount,
            }
        } else if (paymentOptionSelected === 'btc') {
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
            }
        } else {
            alert('Payment type not supported: ' + type);
        }

        paymentModalVisible = true;
    }

    afterNavigate(async () => {
        await waitAndShowLoginIfNotLoggedAlready();
    });

    const nostrPublicKeyUnsubscribe = NostrPublicKey.subscribe(async nostrPublicKeyValue => {
        if (nostrPublicKeyValue) {
            refreshStalls();
            refreshProducts();

            // await new Promise(resolve => setTimeout(resolve, 2500));
            // showAutomaticPayments = true;
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

    function copy(txId) {
        navigator.clipboard.writeText(txId);
        Info.set('Transaction ID copied to clipboard: ' + txId.substring(0,9) + '...');
    }

    onMount(async () => {
        getPaidPaymentsFromStorage();
    });
</script>

<svelte:head>
    <title>Orders</title>
</svelte:head>

<Titleh1>Orders</Titleh1>

{#if Object.keys($privateMessages.automatic).length > 0}
    <div class="grid w-full lg:mx-20 gap-6 lg:gap-10 justify-center items-center place-content-center">
        {#if Object.entries(ordersToBePaidNow).length > 0}
            <div class="alert alert-warning shadow-lg">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    <div>
                        <p class="mb-1">You still have to pay <b>{Object.entries(ordersToBePaidNow).length}</b> of your orders!</p>
                        <ul class="list-disc list-inside ml-3 md:ml-5 text-xs md:text-sm">
                            {#each Object.entries(ordersToBePaidNow) as [_, order]}
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

        <table class="block w-full p-2 md:p-4 rounded border border-gray-400">
            <thead>
            <tr class="text-center">
                <th class="text-left">Order</th>
                <th>Last update</th>
                <th>Status</th>
            </tr>
            </thead>
            <tbody>
            {#each sortedOrders as [orderId, order]}
                {#if order.type !== 10}
                    {#if !hideOldOrders || (hideOldOrders && (Date.now() < ((order.created_at * 1000) + oldOrderTime)))}
                        <tr class="border-y border-gray-600 hover">
                            <td>
                                {#if order.isAuction}
                                    <div class="badge badge-success gap-2">
                                        auction
                                    </div>
                                {:else}
                                    <div class="badge badge-info gap-2">
                                        fixed price
                                    </div>
                                {/if}

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
                                        {#if Array.isArray(order.items)}
                                            {#each order.items as item}
                                                <li>
                                                    <small>
                                                        {#if $products !== null && $products.products[item.product_id]}
                                                            {$products.products[item.product_id].name}
                                                        {:else}
                                                            #{item.product_id}
                                                        {/if}
                                                        {#if item.quantity}
                                                            - {item.quantity} units
                                                        {/if}
                                                    </small>
                                                </li>
                                            {/each}
                                        {:else}
                                            <li>Error loading items from the order</li>
                                        {/if}
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
                                            {#if getAmountToPay(order)}
                                                <p class="mb-2">{getAmountToPay(order)} sats</p>
                                            {/if}

                                            <button class="btn btn-outline gap-2 mb-4 md:mb-2 h-16 md:h-12" on:click|preventDefault={() => {orderToBePaid = order; showPaymentDetails()}}>
                                                <span class="h-7 w-7" ><Bitcoin /></span><p class="-ml-5 text-2xl">⚡</p> Pay order
                                            </button>

                                            {#if order.message && !['Payment received.'].includes(order.message)}
                                                <p class="text-xs lg:text-sm">
                                                    🛈 {order.message}
                                                </p>
                                            {/if}
                                        {/if}
                                    {/if}
                                {:else if order.type === 2}
                                    <p class="text-sm lg:text-base">
                                        {#if order.payment_options}
                                            <ul class="list-disc [&>*:first-child]:block">
                                                {#each order.payment_options as payment_option}
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
                                    <p class="text-sm lg:text-base">
                                        {#if order.shipped}
                                            ✅ Order shipped
                                        {:else}
                                            ❌ Order not shipped yet
                                        {/if}
                                    </p>

                                    {#if order.paid || order.message.includes('TxID:')}
                                        <button class="btn btn-outline btn-primary hover:btn-success h-16 md:h-12 gap-2 mt-4 mb-4 md:mb-2" on:click={() => newNostrConversation(order.pubkey)}>
                                            <span class="w-8 h-8">
                                                <EmailIcon />
                                            </span>
                                            Contact the merchant
                                        </button>
                                    {/if}

                                    {#if order.message && !['Payment received.'].includes(order.message)}
                                        <p class="text-sm text-ellipsis overflow-hidden mt-2">
                                            {#if order.message.includes('TxID:')}
                                                🛈 {order.message.substring(0, order.message.indexOf(' TxID:'))}
                                                <button class="btn btn-xs mt-1" on:click={() => copy(order.message.match(/[^TxID: ]*$/)[0])}>Copy Tx ID</button>
                                            {:else}
                                                🛈 {order.message}
                                            {/if}
                                        </p>
                                    {/if}
                                {:else}
                                    <p>Unknown</p>
                                {/if}

                            </td>
                        </tr>
                    {/if}
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

        {#if orderToBePaid && orderToBePaid.payment_options}
            <div class="mt-4 md:mt-6 pb-0 flex flex-col justify-center items-center">
                Payment type: <select bind:value={paymentOptionSelected} class="select select-bordered select-sm text-xs md:text-sm max-w-lg md:ml-1 { orderToBePaid.payment_options.length > 1 ? 'select-error border-2' : 'select-bordered' }" on:change="{() => showPaymentDetails()}">
                {#each orderToBePaid.payment_options as payment_option}
                    {#if payment_option.type === 'ln'}
                        <option value="{payment_option.type}" selected>Lightning (invoice)</option>
                    {:else if payment_option.type === 'lnurl'}
                        <option value="{payment_option.type}" selected>Lightning (lnurl)</option>
                    {:else if payment_option.type === 'btc'}
                        <option value="{payment_option.type}">Bitcoin (on-chain)</option>
                    {:else if payment_option.type === 'url'}
                        <option value="{payment_option.type}">External payment method</option>
                    {/if}
                {/each}
            </select>
            </div>
        {/if}

        {#if paymentOptionSelected === 'btc'}
            <div class="flex flex-col mt-3 justify-center items-center">
                <div class="h-7 w-7" ><Bitcoin /></div>
            </div>
        {:else if ['ln', 'lnurl'].includes(paymentOptionSelected)}
            <div class="flex flex-col mt-3 justify-center items-center">
                <p class="text-2xl">⚡</p>
            </div>
        {/if}

        {#if paymentInfo.link}
            <div class="py-4 bg-white">
                <QRLocal {paymentInfo} />

                {#if paymentInfo.protocol === 'lightning' && paymentOptionSelected === 'lnurl'}
                    <div class="mt-4 md:mt-6 pb-0 flex flex-col justify-center items-center">
                        <div class="block justify-center items-center mx-auto mb-4">
                            <button class="btn btn-success" on:click|preventDefault={() => paymentConfirmationModalVisible = true}>Mark as paid</button>
                        </div>

                        <ul class="list-disc list-outside text-xs md:text-sm">
                            {#if paymentInfo.amount}
                                <li class="mb-3">You must send <b>{paymentInfo.amount} sats</b> to the seller</li>
                            {/if}
                            <li class="mb-3 md:hidden">You can <b>tap the QR code</b> to open your Lightning wallet.</li>
                            <li class="mb-3">Mark the payment as <b>paid</b> using the green button when you're done.</li>
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
