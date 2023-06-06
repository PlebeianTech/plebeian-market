<script lang="ts">
    import { nip19 } from "nostr-tools";
    import type { IEntity } from "$lib/types/base";
    import { SaleState, type Sale } from "$lib/types/sale";
    import { SATS_IN_BTC } from "$lib/utils";
    import Avatar from "$lib/components/Avatar.svelte";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";

    // svelte-ignore unused-export-let
    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: sale = <Sale>(<unknown>entity);
    $: rate = sale.price_usd * SATS_IN_BTC / sale.price;
    $: extra_usd = sale.tx_value ? rate * (sale.tx_value - sale.amount) / SATS_IN_BTC : 0;
    $: short_title = sale.item_title ? (sale.item_title.length <= 20 ? sale.item_title : sale.item_title.substring(0, 20) + "...") : "";
    $: tx_url = sale.txid ? `https://mempool.space/tx/${sale.txid}` : null;
</script>

<tr>
  <td>
    <DateFormatter date={sale.requested_at} style={DateStyle.Short} />
  </td>
  <td>
    {#if sale.buyer.nostrPublicKey && sale.buyer.nostrPublicKeyVerified}
      <div><a class="link" target="_blank" href="https://snort.social/p/{nip19.npubEncode(sale.buyer.nostrPublicKey)}">{nip19.npubEncode(sale.buyer.nostrPublicKey)}</a></div>
    {:else}
      <div class="flex items-center space-x-3">
        <Avatar account={sale.buyer} />
      </div>
    {/if}
  </td>
  <td>
    <a href={sale.item_url} class:link={sale.item_url !== null}>
      <span title={sale.item_title}>{short_title}</span>
    </a>
  </td>
  <td>
    {sale.amount} / ${sale.price_usd}
  </td>
  <td>
    {#if sale.tx_value}
      {sale.tx_value} (~${extra_usd.toFixed(2)})
    {/if}
  </td>
  <td>
    <div class="badge" class:badge-primary={sale.state === SaleState.TX_CONFIRMED} class:badge-secondary={sale.state !== SaleState.TX_CONFIRMED}>
      <a class="link" title={sale.txid} target="_blank" href={tx_url} rel="noreferrer">
        {sale.stateStr()}
      </a>
    </div>
  </td>
</tr>