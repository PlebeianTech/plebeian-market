<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Sale } from "$lib/types/sale";
    import { SATS_IN_BTC } from "$lib/utils";
    import Avatar from "$lib/components/Avatar.svelte";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";

    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: sale = <Sale>(<unknown>entity);
    $: rate = sale.price_usd * SATS_IN_BTC / sale.price;
    $: extra_usd = sale.tx_value ? rate * (sale.tx_value - sale.amount) / SATS_IN_BTC : 0;
</script>

<tr>
  <td>
    <DateFormatter date={sale.requested_at} style={DateStyle.Short} />
  </td>
  <td>
    {sale.item_title}
  </td>
  <td>
    {sale.quantity}
  </td>
  <td>
    {sale.price_usd}
  </td>
  <td>
    {sale.amount}
  </td>
  <td>
    {#if sale.tx_value}
      {sale.tx_value} (~${extra_usd.toFixed(2)})
    {/if}
  </td>
  <td>
    <div class="flex items-center space-x-3">
      <Avatar account={sale.buyer} />
    </div>
  </td>
  <td>
    <div class="badge badge-primary">
      {sale.stateStr()}
    </div>
  </td>
  <td>
    {#if sale.txid}
      <a class="link" target="_blank" href="https://mempool.space/tx/{sale.txid}">Mempool</a>
    {/if}
  </td>
</tr>