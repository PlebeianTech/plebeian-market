<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Order } from "$lib/types/order";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";
    import { token, Info } from "$lib/stores";
    import { putOrder } from "$lib/services/api";
    import X from "$sharedLib/components/icons/X.svelte";

    // svelte-ignore unused-export-let
    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: order = <Order>(<unknown>entity);
    $: tx_url = order.txid ? `https://mempool.space/tx/${order.txid}` : null;
</script>

<tr>
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
        {#if order.expired_at !== null || order.canceled_at !== null}
            <div class="btn-circle btn-xs btn-error ml-1">
                <X />
            </div>
        {:else if order.shipped_at !== null}
            Shipped!
        {:else}
            {#if order.paid_at === null}
                <button class="btn btn-primary mx-2" on:click={() => putOrder($token, order.uuid, {paid: true}, (o) => {Info.set("Marked as paid!"); entity = o;}) }>Payment received</button>
                <button class="btn btn-error mx-2" on:click={() => putOrder($token, order.uuid, {canceled: true}, (o) => {Info.set("Canceled!"); entity = o;}) }>Cancel</button>
            {:else if order.paid_at !== null && order.shipped_at === null}
                <button class="btn btn-primary" on:click={() => putOrder($token, order.uuid, {shipped: true}, (o) => {Info.set("Marked as shipped!"); entity = o;}) }>Shipped</button>
            {/if}
        {/if}
    </td>
</tr>
