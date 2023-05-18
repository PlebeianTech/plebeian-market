<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Order } from "$lib/types/order";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";

    // svelte-ignore unused-export-let
    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: order = <Order>(<unknown>entity);
    $: tx_url = order.txid ? `https://mempool.space/tx/${order.txid}` : null;
</script>

<tr>
    <td>
        <DateFormatter date={order.requested_at} style={DateStyle.Short} />
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
        {order.txid}
    </td>
</tr>