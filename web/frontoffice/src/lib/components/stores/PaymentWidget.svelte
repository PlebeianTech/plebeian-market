<script>
    import QRLocal from "$lib/components/QRLocal.svelte";
    import Bitcoin from "$sharedLib/components/icons/Bitcoin.svelte";
    import {bech32} from "bech32";
    import {Buffer as BufferPolyfill} from "buffer";
    import {onMount} from "svelte";

    export let orderToBePaid;
    export let showPaymentDetails = showPaymentDetailsForSelectedOption;
    export let paymentConfirmationModalVisible = false;

    let paymentOptionSelected = null;

    let paymentInfo = {
        link: null,
        protocol: null,
        amount: null
    };

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

    function showPaymentDetailsForSelectedOption() {
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
            alert('Payment type not supported: ' + paymentOptionSelected);
        }
    }

    onMount(async () => {
        showPaymentDetailsForSelectedOption();
    });
</script>

{#if orderToBePaid && orderToBePaid.payment_options}
    <div class="mt-4 md:mt-6 pb-0 flex flex-col justify-center items-center">
        Payment type: <select bind:value={paymentOptionSelected} class="select select-bordered select-sm text-xs md:text-sm max-w-lg md:ml-1 { orderToBePaid.payment_options.length > 1 ? 'select-error border-2' : 'select-bordered' }" on:change="{() => showPaymentDetailsForSelectedOption()}">
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