<script lang="ts">
    import { ErrorHandler, putBuy } from "$lib/services/api";
    import { token } from "$lib/stores";
    import { SaleState, type Sale } from "$lib/types/listing";
    import { formatBTC } from "$lib/utils";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import Avatar from "$lib/components/Avatar.svelte";
    import QR from "$lib/components/QR.svelte";

    export let item;

    export let onConfirmed: () => void = () => { };
    export let onExpired: () => void = () => { };

    let sale: Sale | null = null;

    let shippingAmount = 0;

    function domesticShipping() {
        shippingAmount = sale!.shipping_domestic;
    }

    function worldwideShipping() {
        shippingAmount = sale!.shipping_worldwide;
    }

    let waitingResponse = false;
    function buy() {
        waitingResponse = true;
        putBuy($token, item.key,
            (s) => {
                sale = s;
                waitingResponse = false;
            },
            new ErrorHandler(true, () => waitingResponse = false));
    }

    export function onSale(s: Sale) {
        if ((sale && sale.address === s.address) || (sale === null && s.state !== SaleState.TX_CONFIRMED)) {
            sale = s;

            if (sale.state === SaleState.TX_CONFIRMED) {
                onConfirmed();
            }

            if (sale.state === SaleState.EXPIRED) {
                onExpired();
            }
        }
    }
</script>

<div>
    {#if sale && sale.state}
        <ul class="steps steps-vertical lg:steps-horizontal">
            <li class="step" class:step-primary={true}>
                <p class="text-left">Contribution</p>
            </li>
            <li class="step" class:step-primary={sale.state === SaleState.CONTRIBUTION_SETTLED || sale.state === SaleState.TX_DETECTED || sale.state === SaleState.TX_CONFIRMED}>
                <p class="text-left">Payment</p>
            </li>
            <li class="step" class:step-primary={sale.state === SaleState.TX_CONFIRMED}>
                <p class="text-left">Confirmation</p>
            </li>
        </ul>
        {#if sale.state === SaleState.REQUESTED}
            <p class="my-4">The seller wishes to donate <AmountFormatter satsAmount={sale.contribution_amount} /> sats out of the total price to Plebeian Technology. Please send the amount using the QR code below!</p>
            <QR qr={sale.contribution_payment_qr} protocol="lightning" address={sale.contribution_payment_request} />
        {:else if sale.state === SaleState.CONTRIBUTION_SETTLED}
            <p class="my-4">Please send the remaining amount of <AmountFormatter satsAmount={sale.amount} /> plus shipping directly to the seller!</p>
            {#if sale.shipping_domestic !== 0 || sale.shipping_worldwide !== 0}
                <div class="form-control">
                    <label class="label cursor-pointer">
                        <span class="label-text">Domestic shipping <AmountFormatter satsAmount={sale.shipping_domestic} /></span>
                        <input type="radio" name="radio-domestic-shipping" class="radio radio-primary" on:change={domesticShipping} checked={shippingAmount === sale.shipping_domestic} />
                    </label>
                </div>
                <div class="form-control">
                    <label class="label cursor-pointer">
                        <span class="label-text">Worldwide shipping <AmountFormatter satsAmount={sale.shipping_worldwide} /></span>
                        <input type="radio" name="radio-worldwide-shipping" class="radio radio-primary" on:change={worldwideShipping} checked={shippingAmount === sale.shipping_worldwide} />
                    </label>
                </div>
            {/if}
            {#if shippingAmount}
                <p class="text-xl text-center">
                    <AmountFormatter satsAmount={sale.amount} />
                </p>
                <p class="text-center">+</p>
                <p class="text-xl text-center">
                    <AmountFormatter satsAmount={shippingAmount} />
                </p>
                <p class="text-center">=</p>
            {/if}
            <p class="text-2xl text-center mb-4">
                <AmountFormatter satsAmount={sale.amount + shippingAmount} />
            </p>
            <p class="text-txl text-center mb-4">
                BTC {formatBTC(sale.amount + shippingAmount)}
            </p>
            <QR qr={sale.address_qr} protocol="bitcoin" address={sale.address} />
        {:else if sale.state === SaleState.TX_DETECTED}
            <p class="text-2xl text-center my-4">Thank you for your payment!</p>
            <p class="text-xl">Your purchase will be completed when the payment is confirmed by the network.</p>
            <p class="text-xl">In the mean time, you can follow the transaction <a class="link" target="_blank" href="https://mempool.space/tx/{sale.txid}">here</a>!</p>
        {:else if sale.state === SaleState.TX_CONFIRMED}
            <p class="text-3xl text-center my-4">Payment confirmed!</p>
            <p class="text-2xl">Please <a href="/stall/{sale.seller.username}" class="link">contact</a> the seller directly to discuss shipping.</p>
            <p class="text-center mt-4">
                <Avatar account={sale.seller} height="12" />
            </p>
        {/if}
    {:else}
        {#if waitingResponse}
            <button class="btn" disabled>Buy</button>
        {:else}
            <p class="text-3xl text-center pt-12">Price: ~<AmountFormatter usdAmount={item.price_usd} /></p>
            <p class="text-3xl text-center pt-12">{item.available_quantity} items available</p>
            <div class="w-full flex items-center justify-center mt-4">
                <div class="glowbutton glowbutton-buy mt-2" on:click|preventDefault={buy}></div>
            </div>
        {/if}
    {/if}
</div>