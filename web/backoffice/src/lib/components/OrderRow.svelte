<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Order } from "$lib/types/order";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";
    import { Info, token } from "$sharedLib/stores";
    import { putOrder } from "$lib/services/api";
    import X from "$sharedLib/components/icons/X.svelte";

    // svelte-ignore unused-export-let
    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: order = <Order>(<unknown>entity);
    $: tx_url = order.txid ? `https://mempool.space/tx/${order.txid}` : null;

    let buyerModal;
</script>

<tr>
    <td>
        {order.uuid.substring(0, order.uuid.indexOf("-")) + "-..."}
        <button class="btn ml-2 w-20" on:click={() => { navigator.clipboard.writeText(order.uuid) }}>Copy!</button>
    </td>
    <td>
        {#if order.requested_at}
            <DateFormatter date={order.requested_at} style={DateStyle.Short} />
        {/if}
    </td>
    <td>
        {order.total} / ${order.total_usd}
    </td>
    <td>
        {#if order.tx_value}
            {order.tx_value}
        {/if}
    </td>
    <td>
        {#if order.txid}
            <a class="link" href={tx_url} target="_blank">{order.txid}</a>
        {/if}
    </td>
    <td>
        {#if order.expired_at !== null}
            Expired
        {:else if order.canceled_at !== null}
            Canceled
        {:else if order.shipped_at !== null}
            Shipped
        {:else}
            New
        {/if}
    </td>
    <td>
        { order.buyer?.name }
    </td>
    <td>
        <button class="btn" on:click={buyerModal.showModal()}>Details</button>
        <dialog bind:this={buyerModal} class="modal">
            <div class="modal-box w-11/12 max-w-5xl">
                <p class="py-4"><strong>Name</strong>: { order.buyer?.name }</p>
                <p class="py-4"><strong>Address</strong>: { order.buyer?.address }</p>
                {#if order.buyer?.contact}
                    {#each Object.entries(order.buyer?.contact) as [k, v]}
                        <p class="py-4"><strong>{k}</strong>: {v}</p>
                    {/each}
                {/if}
                <p class="py-4"><strong>Message from buyer</strong>: { order.buyer?.message }</p>
                <a class="btn btn-primary ml-2 w-20" href="/messages?newMessagePubKey={order.buyer?.public_key}">Chat!</a>
                <div class="modal-action">
                    <form method="dialog">
                        <button class="btn">close</button>
                    </form>
                </div>
            </div>
        </dialog>
    </td>
    <td>
        {#if order.paid_at === null && order.canceled_at === null}
            <button class="btn btn-error mx-2" on:click={() => putOrder($token, order.uuid, {canceled: true}, (o) => {Info.set("Canceled!"); entity = o;}) }>Cancel</button>
        {:else if order.paid_at !== null && order.shipped_at === null}
            <button class="btn btn-primary" on:click={() => putOrder($token, order.uuid, {shipped: true}, (o) => {Info.set("Marked as shipped!"); entity = o;}) }>Shipped</button>
        {/if}
        {#if order.shipped_at !== null}
            <button class="btn btn-primary mx-2" on:click={() => putOrder($token, order.uuid, {shipped: false}, (o) => {Info.set("Marked as not shipped!"); entity = o;}) }>Not shipped</button>
        {/if}
        {#if order.expired_at !== null}
            <button class="btn btn-primary mx-2" on:click={() => putOrder($token, order.uuid, {expired: false}, (o) => {Info.set("Marked as not expired!"); entity = o;}) }>Not expired</button>
        {/if}
    </td>
</tr>
