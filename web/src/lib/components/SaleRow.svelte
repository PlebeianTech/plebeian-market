<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Sale } from "$lib/types/sale";
    import { SATS_IN_BTC } from "$lib/utils";
    import Avatar from "$lib/components/Avatar.svelte";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";

    // svelte-ignore unused-export-let
    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: sale = <Sale>(<unknown>entity);
    $: rate = sale.price_usd * SATS_IN_BTC / sale.price;
    $: extra_usd = sale.tx_value ? rate * (sale.tx_value - sale.amount) / SATS_IN_BTC : 0;
    $: short_title = sale.item_title.length <= 20 ? sale.item_title : sale.item_title.substring(0, 20) + "...";
</script>

<tr>
  <td>
    <DateFormatter date={sale.requested_at} style={DateStyle.Short} />
  </td>
  <td>
    <span title={sale.item_title}>{short_title}</span>
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
      <a class="link" title={sale.txid} target="_blank" href="https://mempool.space/tx/{sale.txid}">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" width="512.000000pt" height="512.000000pt" viewBox="0 0 2048 2048" >
          <g transform="translate(0.000000,512.000000)">
            <path d="M 1408,608 V 288 Q 1408,169 1323.5,84.5 1239,0 1120,0 H 288 Q 169,0 84.5,84.5 0,169 0,288 v 832 Q 0,1239 84.5,1323.5 169,1408 288,1408 h 704 q 14,0 23,-9 9,-9 9,-23 v -64 q 0,-14 -9,-23 -9,-9 -23,-9 H 288 q -66,0 -113,-47 -47,-47 -47,-113 V 288 q 0,-66 47,-113 47,-47 113,-47 h 832 q 66,0 113,47 47,47 47,113 v 320 q 0,14 9,23 9,9 23,9 h 64 q 14,0 23,-9 9,-9 9,-23 z m 384,864 V 960 q 0,-26 -19,-45 -19,-19 -45,-19 -26,0 -45,19 L 1507,1091 855,439 q -10,-10 -23,-10 -13,0 -23,10 L 695,553 q -10,10 -10,23 0,13 10,23 l 652,652 -176,176 q -19,19 -19,45 0,26 19,45 19,19 45,19 h 512 q 26,0 45,-19 19,-19 19,-45 z" style="fill:currentColor" />
          </g>
        </svg>
      </a>
    {/if}
  </td>
</tr>