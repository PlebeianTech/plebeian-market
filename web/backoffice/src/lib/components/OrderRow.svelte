<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Order } from "$lib/types/order";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";
    import { Info, token } from "$sharedLib/stores";
    import { putOrder } from "$lib/services/api";

    // svelte-ignore unused-export-let
    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: order = <Order>(<unknown>entity);
    $: tx_url = order.txid ? `https://mempool.space/tx/${order.txid}` : null;

    let buyerModal;

    let fiatAmountPrettify: string = "";

    let paymentType: string = "";
    let lnPaymentAt = null;
    let lnPaymentAmount: number = 0;

    $: if (order && order.total_usd && !isNaN(order.total_usd)) {
        if (order.total_usd > 1) {
            fiatAmountPrettify = order.total_usd.toFixed(2);
        } else if (order.total_usd > 99) {
            fiatAmountPrettify = order.total_usd.toFixed(0);
        } else {
            fiatAmountPrettify = order.total_usd.toFixed(5);
        }
    }

    $: if (order.lightning_payment_logs || order.txid) {
        if (order.lightning_payment_logs) {
            console.log('  -- order.lightning_payment_logs', order.lightning_payment_logs);

            order.lightning_payment_logs.forEach(payment_log => {
                console.log('     **** payment_log:', payment_log);
                if (payment_log.type === 1) {
                    lnPaymentAt = payment_log.created_at;
                    lnPaymentAmount = payment_log.amount;
                    paymentType = "BTC_LN";
                }
            });
        } else if (order.txid) {
            paymentType = "BTC_ONCHAIN";
        }
    }
</script>

{(console.log(' ----- order', order), '')}

<tr>
    <td class="pb-5 text-center">
        <div class="tooltip tooltip-info tooltip-right block" data-tip="{order.uuid}">
            <p>{order.uuid.substring(0, order.uuid.indexOf("-")) + "-..."}</p>
        </div>
        <button class="btn btn-xs" on:click={() => { navigator.clipboard.writeText(order.uuid); Info.set("Order ID copied to the clipboard"); }}>Copy</button>
    </td>
    <td class="pb-5 text-center">
        {#if order.requested_at}
            <DateFormatter date={order.requested_at} style={DateStyle.Short} />
        {/if}
    </td>
    <td class="pb-5 text-center">
        <p>
            {order.total} sat
        </p>
        <p>
            ${fiatAmountPrettify}
        </p>
    </td>
    <td class="pb-5">
        {#if paymentType === "BTC_ONCHAIN"}
            <p>Onchain Payment</p>
            <p>
                {#if order.tx_value}
                    {order.tx_value}
                {/if}
            </p>
            <p>
                {#if order.txid}
                    <a class="link" href={tx_url} target="_blank">{order.txid}</a>
                {/if}
            </p>
        {:else if paymentType === "BTC_LN"}
            <p>Lightning Payment</p>
            <p>{lnPaymentAmount} sat to {order.lightning_address}</p>
            <p>{lnPaymentAt}</p>
        {/if}
    </td>
    <td class="pb-5 text-center">
        <p>{ order.buyer?.name ?? '-' }</p>
        <button class="btn btn-xs" on:click={buyerModal.showModal()}>Details</button>
        <dialog bind:this={buyerModal} class="modal">
            <div class="modal-box w-11/12 max-w-5xl">
                <p class="py-4"><strong>Name</strong>: { order.buyer?.name ?? '-' }</p>
                <p class="py-4"><strong>Address</strong>: { order.buyer?.address ?? '-' }</p>
                {#if order.buyer?.contact}
                    {#each Object.entries(order.buyer?.contact) as [k, v]}
                        <p class="py-4"><strong>{k}</strong>: {v}</p>
                    {/each}
                {/if}
                <p class="py-4"><strong>Message from buyer</strong>: { order.buyer?.message ?? '-' }</p>
                <a class="btn btn-primary mt-6" href="/messages?newMessagePubKey={order.buyer?.public_key}">Chat with the buyer</a>
                <div class="modal-action">
                    <form method="dialog">
                        <button class="btn">Close</button>
                    </form>
                </div>
            </div>
        </dialog>
    </td>
    <td class="pb-5 text-center">
        {#if order.shipped_at !== null}
            Shipped
        {:else if order.paid_at !== null}
            Payment Received
        {:else if order.canceled_at !== null}
            Canceled
        {:else if order.expired_at !== null}
            Expired
        {:else}
            Order Received
        {/if}
    </td>
    <td class="pb-5 text-center">
        {#if order.expired_at === null && order.canceled_at === null}
            {#if order.paid_at === null}
                <a class="link link-primary block" on:click={() => putOrder($token, order.uuid, {paid: true}, (o) => {Info.set("Order marked as paid!"); entity = o;}) } href={null}>Mark Payment as received</a>
            {/if}

            {#if order.paid_at !== null && order.shipped_at === null}
                <a class="link link-success block" on:click={() => putOrder($token, order.uuid, {shipped: true}, (o) => {Info.set("Order marked as shipped!"); entity = o;}) } href={null}>Mark order as shipped</a>
            {/if}

            {#if order.shipped_at !== null}
                <a class="link link-primary block" on:click={() => putOrder($token, order.uuid, {shipped: false}, (o) => {Info.set("Order Marked as not shipped!"); entity = o;}) } href={null}>Mark as Not Shipped</a>
            {/if}

            {#if order.paid_at === null && order.shipped_at === null}
                <a class="link link-error block" on:click={() => putOrder($token, order.uuid, {canceled: true}, (o) => {Info.set("Canceled!"); entity = o;}) } href={null}>Cancel Order</a>
            {/if}
        {:else}
            <!--
            <p>
                Recover Order <a class="link link-primary block" on:click={() => putOrder($token, order.uuid, {expired: false}, (o) => {Info.set("Marked as not expired!"); entity = o;}) }>(mark as Not Expired)</a>
            </p>
            -->
        {/if}
    </td>
</tr>
