<script lang="ts">
    import { Category, type Item } from "$lib/types/item";
    import { SaleState, type Sale } from "$lib/types/sale";
    import { formatBTC } from "$lib/utils";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import Avatar, { AvatarSize } from "$lib/components/Avatar.svelte";
    import QR from "$lib/components/QR.svelte";

    export let item: Item;
    export let sale: Sale;

    $: hasShipping = sale.shipping_domestic !== 0 || sale.shipping_worldwide !== 0;

    let shippingAmount = sale.shipping_worldwide;
    let qr = sale.qr;

    function domesticShipping() {
        shippingAmount = sale.shipping_domestic;
        qr = sale.qr_domestic;
    }

    function worldwideShipping() {
        shippingAmount = sale.shipping_worldwide;
        qr = sale.qr_worldwide;
    }
</script>

<div class="flex justify-center">

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
</div>

{#if sale.state === SaleState.REQUESTED}
    <p class="my-4">The seller wishes to donate <AmountFormatter satsAmount={sale.contribution_amount} /> sats out of the total price to Plebeian Technology. Please send the amount using the QR code below!</p>
    <QR qr={sale.contribution_payment_qr} protocol="lightning" address={sale.contribution_payment_request} />
{:else if sale.state === SaleState.CONTRIBUTION_SETTLED}
    {#if sale.contribution_amount !== 0}
        <p class="text-xl my-4">
            Thank you for your contribution!
        </p>
    {/if}
    <p class="my-4">
        Please send the
        {#if sale.contribution_amount !== 0}remaining {/if}
        amount of <AmountFormatter satsAmount={sale.amount} />
        {#if hasShipping}plus shipping {/if}
        directly to
        {#if item.campaign_name !== null}
            <div class="badge badge-primary mb-4"><a href="/campaigns/{item.campaign_key}">{item.campaign_name} campaign</a></div>
        {:else}
            the seller
        {/if}
        !
    </p>
    {#if hasShipping}
        {#if sale.shipping_domestic === sale.shipping_worldwide}
            <div class="form-control">
                <label class="label cursor-pointer">
                    <span class="label-text">Shipping <AmountFormatter satsAmount={sale.shipping_domestic} /></span>
                    <input type="radio" name="radio-domestic-shipping" class="radio radio-primary" checked={true} />
                </label>
            </div>
        {:else}
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
    {/if}
    {#if shippingAmount}
        <p class="text-xl text-center mt-4">
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
    <p class="text-2xl text-center mb-4">
        Pay on-chain!
    </p>
    <QR {qr} protocol="bitcoin" address={sale.address} />
{:else if sale.state === SaleState.TX_DETECTED || sale.state === SaleState.TX_CONFIRMED}
    <p class="text-2xl text-center my-4">Thank you for your payment!</p>
    <div class="alert alert-info shadow-lg my-4">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>
                TxID: <a class="link break-all" target="_blank" href="https://mempool.space/tx/{sale.txid}" rel="noreferrer">{sale.txid}</a>
            </span>
        </div>
    </div>
    {#if sale.state === SaleState.TX_DETECTED}
        <p class="text-xl">Your purchase will be completed when the payment is confirmed by the network.</p>
        <p class="text-xl">In the meantime, you can follow the transaction on <a class="link" target="_blank" href="https://mempool.space/tx/{sale.txid}" rel="noreferrer">mempool.space</a>!</p>
    {:else}
        <p class="text-3xl text-center my-10">Payment confirmed!</p>
        <div class="grid place-items-center space-y-4 mb-8">
          <p class="text-2xl">
              Please <a href="/stall/{sale.seller.nym}" class="link">contact</a>
              the seller directly
              {#if item.category !== Category.Time}
                  to discuss shipping
              {/if}
          </p>
          <div class="text-center">
              <Avatar account={sale.seller} size={AvatarSize.M} />
          </div>
        </div>
    {/if}
{/if}
