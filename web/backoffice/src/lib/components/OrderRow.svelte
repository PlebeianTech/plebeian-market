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
</script>

{(console.log(' ----- order', order), '')}

<tr>
    <td class="pb-4">
        <div class="tooltip tooltip-open tooltip-info" data-tip="{order.uuid}">
            <p>{order.uuid.substring(0, order.uuid.indexOf("-")) + "-..."}</p>
        </div>
        <button class="btn btn-xs" on:click={() => { navigator.clipboard.writeText(order.uuid) }}>Copy</button>
    </td>
    <td class="pb-4 text-center">
        {#if order.requested_at}
            <DateFormatter date={order.requested_at} style={DateStyle.Short} />
        {/if}
    </td>
    <td class="pb-4 text-center">
        {order.total} / ${order.total_usd}
    </td>
    <td class="pb-4">
        {#if order.tx_value}
            {order.tx_value}
        {/if}
    </td>
    <td class="pb-4">
        {#if order.txid}
            <a class="link" href={tx_url} target="_blank">{order.txid}</a>
        {/if}
    </td>
    <td class="pb-4 text-center">
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
    <td class="pb-4 text-center">
        {#if order.paid_at !== null}
            Payment Received
        {:else if order.expired_at !== null}
            Expired
        {:else if order.canceled_at !== null}
            Canceled
        {:else if order.shipped_at !== null}
            Shipped
        {:else}
            Order Received
        {/if}
    </td>
    <td class="pb-4">
        {#if order.expired_at !== null}
            {#if order.canceled_at !== null}

            {/if}

            {#if order.paid_at === null && order.canceled_at === null}
                <a class="link link-primary block" on:click={() => putOrder($token, order.uuid, {paid: true}, (o) => {Info.set("Paid!"); entity = o;}) }>Mark Payment as received</a>
            {/if}

            {#if order.paid_at !== null && order.shipped_at === null}
                <a class="link link-success block" on:click={() => putOrder($token, order.uuid, {shipped: true}, (o) => {Info.set("Marked as shipped!"); entity = o;}) } href={null}>Mark order as shipped</a>
            {/if}

            {#if order.shipped_at !== null}
                Order Shipped. <a class="link link-primary block" on:click={() => putOrder($token, order.uuid, {shipped: false}, (o) => {Info.set("Marked as not shipped!"); entity = o;}) }>Mark Order as Not Shipped</a>
            {/if}

            {#if order.canceled_at === null}
                <a class="link link-error block" on:click={() => putOrder($token, order.uuid, {canceled: true}, (o) => {Info.set("Canceled!"); entity = o;}) } href={null}>Cancel Order</a>
            {/if}
        {:else}
            {#if order.expired_at !== null}
                <p>
                    Recover Order <a class="link link-primary block" on:click={() => putOrder($token, order.uuid, {expired: false}, (o) => {Info.set("Marked as not expired!"); entity = o;}) }>(mark as Not Expired)</a>
                </p>
            {/if}
        {/if}
    </td>
</tr>
